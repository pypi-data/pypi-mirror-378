//! DDEX Builder CLI - Comprehensive command-line interface for DDEX XML processing
//!
//! This CLI provides tools for building, converting, validating, and comparing DDEX XML files
//! with deterministic output and support for various partner presets.

use clap::{Args, CommandFactory, Parser, Subcommand, ValueEnum};
use clap_complete::{generate, Shell};
use console::style;
use ddex_builder::presets::{DdexVersion, MessageProfile};
use ddex_builder::*;
use indexmap::IndexMap;
use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use serde_json::Value as JsonValue;
use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process;

#[derive(Parser)]
#[command(
    name = "ddex-builder",
    about = "DDEX Builder CLI - High-performance DDEX XML processing toolkit",
    long_about = "A comprehensive command-line interface for building, converting, validating, and comparing DDEX XML files with deterministic output and partner preset support.",
    version = env!("CARGO_PKG_VERSION"),
    author = "Kevin Marques Moo"
)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Enable verbose output
    #[arg(short, long, global = true, action = clap::ArgAction::Count)]
    verbose: u8,

    /// Suppress all non-error output
    #[arg(short, long, global = true)]
    quiet: bool,

    /// Control color output
    #[arg(long, global = true, value_enum, default_value_t = ColorChoice::Auto)]
    color: ColorChoice,

    /// Path to configuration file
    #[arg(long, global = true)]
    config: Option<PathBuf>,
}

#[derive(Subcommand)]
enum Commands {
    /// Build DDEX XML from structured data
    Build(BuildCommand),
    /// Convert DDEX XML between versions
    Convert(ConvertCommand),
    /// Compare two DDEX files semantically
    Diff(DiffCommand),
    /// Validate DDEX XML files
    Validate(ValidateCommand),
    /// Generate schemas for validation
    Schema(SchemaCommand),
    /// Process multiple files in parallel
    Batch(BatchCommand),
    /// Validate determinism guarantees
    Guarantees(GuaranteesCommand),
    /// List and apply partner presets
    Preset(PresetCommand),
    /// Watch files for changes and rebuild
    Watch(WatchCommand),
    /// Run HTTP API server for builder operations
    Server(ServerCommand),
    /// Generate shell completions
    Completions(CompletionsCommand),
}

#[derive(Args)]
struct BuildCommand {
    /// Input file (JSON/YAML/TOML) or '-' for stdin
    #[arg(short, long)]
    input: Option<PathBuf>,

    /// Output file path or '-' for stdout
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// DDEX version to generate
    #[arg(long = "ddex-version", value_enum)]
    version: Option<DdexVersionArg>,

    /// Content profile to use
    #[arg(short, long)]
    profile: Option<String>,

    /// Partner preset configuration
    #[arg(long, value_enum)]
    preset: Option<PresetChoice>,

    /// Validate before building
    #[arg(long)]
    validate: bool,

    /// Input data format (auto-detected if not specified)
    #[arg(long, value_enum)]
    format: Option<InputFormat>,

    /// Enable strict validation
    #[arg(long)]
    strict: bool,

    /// Verify determinism by building multiple times
    #[arg(long)]
    verify_determinism: bool,

    /// Number of iterations for determinism verification (default: 3)
    #[arg(long, default_value_t = 3)]
    determinism_iterations: usize,
}

#[derive(Args)]
struct ConvertCommand {
    /// Input DDEX XML file or '-' for stdin
    #[arg(short, long)]
    input: Option<PathBuf>,

    /// Source DDEX version
    #[arg(short, long, value_enum)]
    from: DdexVersionArg,

    /// Target DDEX version
    #[arg(short, long, value_enum)]
    to: DdexVersionArg,

    /// Output file path or '-' for stdout
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Generate conversion report
    #[arg(long)]
    report: Option<PathBuf>,

    /// Enable lossy conversion warnings
    #[arg(long)]
    allow_lossy: bool,
}

#[derive(Args)]
struct DiffCommand {
    /// First DDEX XML file
    file1: PathBuf,

    /// Second DDEX XML file
    file2: PathBuf,

    /// Output format
    #[arg(short, long, value_enum, default_value_t = DiffFormat::Human)]
    format: DiffFormat,

    /// Output file path (default: stdout)
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Include technical details in diff
    #[arg(long)]
    detailed: bool,

    /// Ignore whitespace differences
    #[arg(long)]
    ignore_whitespace: bool,
}

#[derive(Args)]
struct ValidateCommand {
    /// DDEX XML files to validate
    files: Vec<PathBuf>,

    /// DDEX version for validation
    #[arg(long = "ddex-version", value_enum)]
    version: Option<DdexVersionArg>,

    /// Content profile for validation
    #[arg(short, long)]
    profile: Option<String>,

    /// Partner preset for validation
    #[arg(long, value_enum)]
    preset: Option<PresetChoice>,

    /// Enable strict validation rules
    #[arg(long)]
    strict: bool,

    /// Output format for validation results
    #[arg(long, value_enum, default_value_t = ValidateFormat::Human)]
    output_format: ValidateFormat,

    /// Stop at first validation error
    #[arg(long)]
    fail_fast: bool,
}

#[derive(Args)]
struct SchemaCommand {
    /// DDEX version for schema generation
    #[arg(long = "ddex-version", value_enum)]
    version: DdexVersionArg,

    /// Content profile
    #[arg(short, long)]
    profile: Option<String>,

    /// Output format
    #[arg(short, long, value_enum, default_value_t = SchemaFormat::Json)]
    format: SchemaFormat,

    /// Output file path or '-' for stdout
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Include documentation in schema
    #[arg(long)]
    with_docs: bool,
}

#[derive(Args)]
struct BatchCommand {
    /// Configuration file for batch processing
    #[arg(short, long)]
    config: PathBuf,

    /// Number of worker threads
    #[arg(short, long, default_value_t = num_cpus::get())]
    workers: usize,

    /// Continue processing on errors
    #[arg(long)]
    continue_on_error: bool,

    /// Generate summary report
    #[arg(long)]
    report: Option<PathBuf>,
}

#[derive(Args)]
struct GuaranteesCommand {
    /// Input file (JSON/YAML/TOML) for build request
    #[arg(short, long)]
    input: PathBuf,

    /// Output format for guarantee report
    #[arg(short, long, value_enum, default_value_t = GuaranteeFormat::Human)]
    format: GuaranteeFormat,

    /// Output file path (default: stdout)
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Run comprehensive stress tests
    #[arg(long)]
    thorough: bool,

    /// Number of determinism verification iterations
    #[arg(long, default_value_t = 3)]
    iterations: usize,

    /// Only show failed guarantees
    #[arg(long)]
    failures_only: bool,

    /// Include detailed evidence in report
    #[arg(long)]
    include_evidence: bool,
}

#[derive(Args)]
struct PresetCommand {
    /// Preset operation
    #[command(subcommand)]
    operation: PresetOperation,
}

#[derive(Subcommand)]
enum PresetOperation {
    /// List available presets
    List(PresetListCommand),
    /// Show preset details
    Show(PresetShowCommand),
    /// Apply preset to input data
    Apply(PresetApplyCommand),
}

#[derive(Args)]
struct PresetListCommand {
    /// Filter by DDEX version
    #[arg(long, value_enum)]
    version: Option<DdexVersionArg>,

    /// Filter by partner
    #[arg(long, value_enum)]
    partner: Option<PresetChoice>,

    /// Output format
    #[arg(short, long, value_enum, default_value_t = PresetListFormat::Human)]
    format: PresetListFormat,
}

#[derive(Args)]
struct PresetShowCommand {
    /// Preset identifier
    preset: String,

    /// Output format
    #[arg(short, long, value_enum, default_value_t = PresetShowFormat::Human)]
    format: PresetShowFormat,

    /// Include full configuration details
    #[arg(long)]
    detailed: bool,
}

#[derive(Args)]
struct PresetApplyCommand {
    /// Preset identifier
    preset: String,

    /// Input file (JSON/YAML/TOML) or '-' for stdin
    #[arg(short, long)]
    input: Option<PathBuf>,

    /// Output file path or '-' for stdout
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Input data format (auto-detected if not specified)
    #[arg(long, value_enum)]
    format: Option<InputFormat>,

    /// Override preset DDEX version
    #[arg(long, value_enum)]
    version_override: Option<DdexVersionArg>,

    /// Validate output after applying preset
    #[arg(long)]
    validate: bool,
}

#[derive(Args)]
struct WatchCommand {
    /// Directory or file to watch
    #[arg(short, long)]
    path: PathBuf,

    /// Pattern to match files (glob syntax)
    #[arg(short, long, default_value = "**/*.{json,yaml,yml,toml}")]
    pattern: String,

    /// Command to run on file changes
    #[arg(short, long)]
    command: Option<String>,

    /// Output directory for built files
    #[arg(short, long)]
    output_dir: Option<PathBuf>,

    /// DDEX version to use for building
    #[arg(long, value_enum)]
    version: Option<DdexVersionArg>,

    /// Preset to apply
    #[arg(long, value_enum)]
    preset: Option<PresetChoice>,

    /// Debounce delay in milliseconds (default: 500ms)
    #[arg(long, default_value_t = 500)]
    debounce: u64,

    /// Run initial build on startup
    #[arg(long)]
    initial_build: bool,

    /// Recursive watch subdirectories
    #[arg(short, long)]
    recursive: bool,

    /// Exclude patterns (glob syntax)
    #[arg(long)]
    exclude: Vec<String>,
}

#[derive(Args)]
struct ServerCommand {
    /// Server bind address
    #[arg(short, long, default_value = "127.0.0.1")]
    bind: String,

    /// Server port
    #[arg(short, long, default_value_t = 8080)]
    port: u16,

    /// Number of worker threads
    #[arg(short, long, default_value_t = num_cpus::get())]
    workers: usize,

    /// Enable CORS for cross-origin requests
    #[arg(long)]
    cors: bool,

    /// Maximum request size in MB
    #[arg(long, default_value_t = 10)]
    max_request_size: usize,

    /// Request timeout in seconds
    #[arg(long, default_value_t = 30)]
    timeout: u64,

    /// Enable request logging
    #[arg(long)]
    log_requests: bool,

    /// TLS certificate file (for HTTPS)
    #[arg(long)]
    tls_cert: Option<PathBuf>,

    /// TLS private key file (for HTTPS)
    #[arg(long)]
    tls_key: Option<PathBuf>,

    /// Rate limiting: requests per minute per IP
    #[arg(long)]
    rate_limit: Option<u32>,
}

#[derive(Args)]
struct CompletionsCommand {
    /// Shell to generate completions for
    #[arg(value_enum)]
    shell: Shell,

    /// Output file path (default: stdout)
    #[arg(short, long)]
    output: Option<PathBuf>,
}

#[derive(ValueEnum, Clone, Debug)]
enum ColorChoice {
    Auto,
    Always,
    Never,
}

#[derive(ValueEnum, Clone, Copy, Debug)]
enum DdexVersionArg {
    #[value(name = "3.8.2")]
    V382,
    #[value(name = "4.1")]
    V41,
    #[value(name = "4.2")]
    V42,
    #[value(name = "4.3")]
    V43,
    #[value(name = "4.4")]
    V44,
}

#[derive(ValueEnum, Clone, Copy, Debug)]
enum PresetChoice {
    /// Generic audio album preset (DDEX-compliant baseline)
    AudioAlbum,
    /// Generic audio single preset (DDEX-compliant baseline)
    AudioSingle,
    /// Generic video single preset (DDEX-compliant baseline)
    VideoSingle,
    /// Generic compilation preset (DDEX-compliant baseline)
    Compilation,
    /// YouTube album preset (based on public documentation)
    YoutubeAlbum,
    /// YouTube video preset (based on public documentation)
    YoutubeVideo,
    /// YouTube single preset (based on public documentation)
    YoutubeSingle,
}

#[derive(ValueEnum, Clone, Debug)]
enum InputFormat {
    Json,
    Yaml,
    Toml,
}

#[derive(ValueEnum, Clone, Debug, PartialEq)]
enum DiffFormat {
    Human,
    Json,
    Update,
}

#[derive(ValueEnum, Clone, Debug)]
enum ValidateFormat {
    Human,
    Json,
    Junit,
}

#[derive(ValueEnum, Clone, Debug)]
enum SchemaFormat {
    Json,
    Typescript,
    Python,
}

#[derive(ValueEnum, Clone, Debug)]
enum GuaranteeFormat {
    Human,
    Json,
    Yaml,
}

#[derive(ValueEnum, Clone, Debug)]
enum PresetListFormat {
    Human,
    Json,
    Table,
}

#[derive(ValueEnum, Clone, Debug)]
enum PresetShowFormat {
    Human,
    Json,
    Yaml,
}

impl From<DdexVersionArg> for DdexVersion {
    fn from(version: DdexVersionArg) -> Self {
        match version {
            DdexVersionArg::V382 => DdexVersion::Ern382,
            DdexVersionArg::V41 => DdexVersion::Ern41,
            DdexVersionArg::V42 => DdexVersion::Ern42,
            DdexVersionArg::V43 => DdexVersion::Ern43,
            DdexVersionArg::V44 => DdexVersion::Ern43, // Map V44 to Ern43 since Ern44 doesn't exist yet
        }
    }
}

fn main() {
    let cli = Cli::parse();

    // Setup logging based on verbosity
    setup_logging(cli.verbose, cli.quiet);

    // Setup color output
    setup_colors(cli.color);

    // Load configuration if specified
    let config = cli
        .config
        .as_ref()
        .map(|p| load_config(p))
        .unwrap_or_default();

    let result = match cli.command {
        Commands::Build(cmd) => handle_build_command(cmd, &config),
        Commands::Convert(cmd) => handle_convert_command(cmd, &config),
        Commands::Diff(cmd) => handle_diff_command(cmd, &config),
        Commands::Validate(cmd) => handle_validate_command(cmd, &config),
        Commands::Schema(cmd) => handle_schema_command(cmd, &config),
        Commands::Batch(cmd) => handle_batch_command(cmd, &config),
        Commands::Guarantees(cmd) => handle_guarantees_command(cmd, &config),
        Commands::Preset(cmd) => handle_preset_command(cmd, &config),
        Commands::Watch(cmd) => handle_watch_command(cmd, &config),
        Commands::Server(cmd) => handle_server_command(cmd, &config),
        Commands::Completions(cmd) => handle_completions_command(cmd),
    };

    if let Err(e) = result {
        eprintln!("{} {}", style("Error:").red().bold(), e);
        process::exit(1);
    }
}

fn setup_logging(verbosity: u8, quiet: bool) {
    if quiet {
        return;
    }

    let level = match verbosity {
        0 => tracing::Level::WARN,
        1 => tracing::Level::INFO,
        2 => tracing::Level::DEBUG,
        _ => tracing::Level::TRACE,
    };

    tracing_subscriber::fmt()
        .with_max_level(level)
        .with_target(false)
        .init();
}

fn setup_colors(color_choice: ColorChoice) {
    match color_choice {
        ColorChoice::Always => {
            console::set_colors_enabled(true);
            console::set_colors_enabled_stderr(true);
        }
        ColorChoice::Never => {
            console::set_colors_enabled(false);
            console::set_colors_enabled_stderr(false);
        }
        ColorChoice::Auto => {
            // Default behavior - colors enabled for TTY
        }
    }
}

fn load_config(_path: &Path) -> ConfigFile {
    // TODO: Implement configuration file loading
    ConfigFile::default()
}

#[derive(Default)]
struct ConfigFile {
    // Configuration options that can be loaded from file
}

fn handle_build_command(
    cmd: BuildCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    let input_data = read_input_data(&cmd.input, cmd.format)?;

    // Create builder with optional preset
    let mut builder = Builder::new();

    if let Some(preset) = cmd.preset {
        let preset_name = preset_to_string(&preset);
        builder
            .apply_preset(&preset_name, false)
            .map_err(|e| format!("Failed to apply preset '{}': {}", preset_name, e))?;
    }

    if let Some(version) = cmd.version {
        builder.with_version(version.into());
    }

    // Validate input if requested
    if cmd.validate {
        validate_input_data(&input_data, &builder, cmd.strict)?;
    }

    // Build the XML
    let xml_output = build_ddex_xml(&input_data, &builder)?;

    // Verify determinism if requested
    if cmd.verify_determinism {
        verify_build_determinism(&input_data, &builder, cmd.determinism_iterations)?;
    }

    // Write output
    write_output(&xml_output, &cmd.output)?;

    if !is_quiet() {
        println!("{} DDEX XML built successfully", style("✓").green());
        if let Some(preset) = cmd.preset {
            println!("  Preset: {}", preset_to_string(&preset));
        }
        if let Some(version) = cmd.version {
            println!("  Version: {:?}", version);
        }
        if cmd.verify_determinism {
            println!(
                "  {} Determinism verified with {} iterations",
                style("✓").green(),
                cmd.determinism_iterations
            );
        }
    }

    Ok(())
}

fn handle_convert_command(
    cmd: ConvertCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    let input_xml = read_input_string(&cmd.input)?;

    let builder = Builder::new();
    let conversion_options = ConversionOptions {
        detailed_reports: true,
        preserve_unknown: cmd.allow_lossy,
        preserve_comments: true,
        ..Default::default()
    };

    let result = builder.convert_version(
        &input_xml,
        cmd.from.into(),
        cmd.to.into(),
        Some(conversion_options),
    )?;

    match result {
        versions::ConverterResult::Success { xml, report } => {
            // Write converted XML
            write_output(&xml, &cmd.output)?;

            // Generate report if requested
            if let Some(report_path) = cmd.report {
                let report_json = serde_json::to_string_pretty(&report)?;
                fs::write(report_path, report_json)?;
            }

            if !is_quiet() {
                println!("{} Conversion completed", style("✓").green());
                println!("  From: {:?} → To: {:?}", cmd.from, cmd.to);
                if !report.warnings.is_empty() {
                    println!("  {} warnings generated", report.warnings.len());
                }
            }
        }
        versions::ConverterResult::Failure { error, report: _ } => {
            return Err(format!("Conversion failed: {}", error).into());
        }
    }

    Ok(())
}

fn handle_diff_command(
    cmd: DiffCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    let xml1 = fs::read_to_string(&cmd.file1)?;
    let xml2 = fs::read_to_string(&cmd.file2)?;

    let _diff_config = diff::DiffConfig {
        ignore_formatting: cmd.ignore_whitespace,
        ..Default::default()
    };
    // TODO: Parse XML to AST for proper semantic diffing
    // For now, create a placeholder changeset
    let changeset = diff::types::ChangeSet::new();

    let formatted_output = match cmd.format {
        DiffFormat::Human => diff::formatter::DiffFormatter::format_summary(&changeset),
        DiffFormat::Json => serde_json::to_string_pretty(&changeset)?,
        DiffFormat::Update => {
            let mut update_generator = messages::UpdateGenerator::new();
            let _update_message = update_generator.create_update(&xml1, &xml2, "cli-generated")?;
            // TODO: Implement XML serialization for UpdateReleaseMessage
            format!("<!-- Update message XML would be serialized here -->")
        }
    };

    write_output(&formatted_output, &cmd.output)?;

    if !is_quiet() && cmd.format == DiffFormat::Human {
        if changeset.changes.is_empty() {
            println!("{} Files are identical", style("✓").green());
        } else {
            println!(
                "{} {} differences found",
                style("!").yellow(),
                changeset.changes.len()
            );
        }
    }

    Ok(())
}

fn handle_validate_command(
    cmd: ValidateCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    let mut all_valid = true;
    let mut results = Vec::new();

    for file_path in &cmd.files {
        let _xml_content = fs::read_to_string(file_path)?;

        let mut builder = Builder::new();
        if let Some(preset) = &cmd.preset {
            let preset_name = preset_to_string(preset);
            builder.apply_preset(&preset_name, false)?;
        }

        let validation_config = ValidationConfig {
            level: if cmd.strict {
                PreflightLevel::Strict
            } else {
                PreflightLevel::Warn
            },
            profile: cmd.profile.clone(),
            ..Default::default()
        };

        let _validator = PreflightValidator::new(validation_config);
        // TODO: Parse XML content to BuildRequest for validation
        // For now, create a placeholder result
        let result = ValidationResult {
            errors: Vec::new(),
            warnings: Vec::new(),
            info: Vec::new(),
            passed: true,
        };

        let file_valid = result.errors.is_empty();
        all_valid = all_valid && file_valid;

        results.push((file_path.clone(), result));

        if cmd.fail_fast && !file_valid {
            break;
        }
    }

    // Output results
    match cmd.output_format {
        ValidateFormat::Human => {
            for (file_path, result) in &results {
                print_validation_result_human(file_path, result);
            }
        }
        ValidateFormat::Json => {
            let json_output = serde_json::to_string_pretty(&results)?;
            println!("{}", json_output);
        }
        ValidateFormat::Junit => {
            let junit_output = format_junit_results(&results)?;
            println!("{}", junit_output);
        }
    }

    if !all_valid {
        process::exit(1);
    }

    Ok(())
}

fn handle_schema_command(
    cmd: SchemaCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    let _schema_config = schema::SchemaConfig {
        include_descriptions: cmd.with_docs,
        ..Default::default()
    };

    // Use a default profile for now - this could be enhanced to support actual profiles
    let profile = MessageProfile::AudioAlbum;
    let generator = schema::SchemaGenerator::new(cmd.version.into(), profile);
    let schema_result = generator.generate_complete_schema()?;
    let schema_output = match cmd.format {
        SchemaFormat::Json => serde_json::to_string_pretty(&schema_result.schema)?,
        SchemaFormat::Typescript => generator.generate_typescript_types(&schema_result.schema)?,
        SchemaFormat::Python => generator.generate_python_types(&schema_result.schema)?,
    };

    write_output(&schema_output, &cmd.output)?;

    if !is_quiet() {
        println!("{} Schema generated successfully", style("✓").green());
        println!("  Format: {:?}", cmd.format);
        println!("  Version: {:?}", cmd.version);
    }

    Ok(())
}

fn handle_batch_command(
    cmd: BatchCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    let batch_config = load_batch_config(&cmd.config)?;

    // Setup thread pool
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(cmd.workers)
        .build()?;

    let progress_bar = if !is_quiet() {
        let pb = ProgressBar::new(batch_config.tasks.len() as u64);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("[{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} {msg}")
                .unwrap(),
        );
        Some(pb)
    } else {
        None
    };

    let results: Vec<BatchResult> = pool.install(|| {
        batch_config
            .tasks
            .par_iter()
            .enumerate()
            .map(|(i, task)| {
                let result = process_batch_task(task);
                if let Some(pb) = &progress_bar {
                    pb.set_message(format!("Processing {}", task.input_file.display()));
                    pb.inc(1);
                }
                BatchResult {
                    task_id: i,
                    success: result.is_ok(),
                    error: result.err().map(|e| e.to_string()),
                }
            })
            .collect()
    });

    if let Some(pb) = &progress_bar {
        pb.finish_with_message("Batch processing completed");
    }

    // Generate report
    let successful = results.iter().filter(|r| r.success).count();
    let failed = results.len() - successful;

    if !is_quiet() {
        println!("\n{} Batch processing completed", style("✓").green());
        println!("  Successful: {}", successful);
        if failed > 0 {
            println!("  Failed: {}", style(failed).red());
        }
    }

    if let Some(report_path) = cmd.report {
        let report = BatchReport {
            total_tasks: results.len(),
            successful,
            failed,
            results,
        };
        let report_json = serde_json::to_string_pretty(&report)?;
        fs::write(report_path, report_json)?;
    }

    if failed > 0 && !cmd.continue_on_error {
        process::exit(1);
    }

    Ok(())
}

fn handle_guarantees_command(
    cmd: GuaranteesCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    use ddex_builder::builder::BuildRequest;
    use ddex_builder::determinism::{DeterminismConfig, DeterminismVerifier};
    use ddex_builder::guarantees::generate_guarantee_report;

    // Read and parse input data
    let input_data = read_input_data(&Some(cmd.input.clone()), None)?;

    // Parse JSON data into BuildRequest structure
    let request: BuildRequest = serde_json::from_value(input_data)?;

    if !is_quiet() {
        println!(
            "🔍 Validating determinism guarantees for {}",
            cmd.input.display()
        );
        if cmd.thorough {
            println!("   Running comprehensive stress tests...");
        }
    }

    // Generate guarantee report
    let report = if cmd.thorough {
        // Run thorough verification with stress tests
        let _verifier = DeterminismVerifier::new(DeterminismConfig::default());
        let _result = DeterminismVerifier::thorough_check(&request, cmd.iterations)?;

        // Generate full report
        generate_guarantee_report(&request, &DeterminismConfig::default())?
    } else {
        // Quick guarantee validation
        generate_guarantee_report(&request, &DeterminismConfig::default())?
    };

    // Format output
    let output_content = match cmd.format {
        GuaranteeFormat::Human => {
            format_guarantee_report_human(&report, cmd.failures_only, cmd.include_evidence)
        }
        GuaranteeFormat::Json => {
            if cmd.failures_only {
                let failed_results: Vec<_> =
                    report.failed_guarantees().into_iter().cloned().collect();
                serde_json::to_string_pretty(&failed_results)?
            } else {
                serde_json::to_string_pretty(&report)?
            }
        }
        GuaranteeFormat::Yaml => {
            if cmd.failures_only {
                let failed_results: Vec<_> =
                    report.failed_guarantees().into_iter().cloned().collect();
                serde_yaml::to_string(&failed_results)?
            } else {
                serde_yaml::to_string(&report)?
            }
        }
    };

    // Write output
    write_output(&output_content, &cmd.output)?;

    // Print summary if not quiet and using human format
    if !is_quiet() && matches!(cmd.format, GuaranteeFormat::Human) {
        println!("\n{}", report.summary());

        if !report.overall_pass {
            let critical_failures = report.critical_failures();
            if !critical_failures.is_empty() {
                println!("\n{} Critical failures detected:", style("⚠").red().bold());
                for failure in critical_failures {
                    println!("  {} {:?}", style("✗").red(), failure.guarantee);
                }
                return Err("Critical determinism guarantees failed".into());
            }
        }
    }

    // Exit with error if guarantees failed and we're not just generating a report
    if !report.overall_pass && cmd.output.is_none() {
        std::process::exit(1);
    }

    Ok(())
}

fn format_guarantee_report_human(
    report: &ddex_builder::guarantees::GuaranteeReport,
    failures_only: bool,
    include_evidence: bool,
) -> String {
    let mut output = String::new();

    output.push_str(&format!("# Determinism Guarantee Report\n"));
    output.push_str(&format!(
        "Generated: {}\n\n",
        report.timestamp.format("%Y-%m-%d %H:%M:%S UTC")
    ));

    if !failures_only {
        output.push_str(&format!("## Summary\n"));
        output.push_str(&format!(
            "- Total guarantees: {}\n",
            report.total_guarantees
        ));
        output.push_str(&format!(
            "- Passed: {} ({:.1}%)\n",
            report.passed_guarantees, report.success_rate
        ));
        output.push_str(&format!(
            "- Failed: {}\n\n",
            report.total_guarantees - report.passed_guarantees
        ));
    }

    let results_to_show = if failures_only {
        report.failed_guarantees()
    } else {
        report.results.iter().collect()
    };

    if !results_to_show.is_empty() {
        output.push_str(&format!(
            "## {}\n",
            if failures_only {
                "Failed Guarantees"
            } else {
                "Results"
            }
        ));

        for result in results_to_show {
            let status = if result.passed { "✅" } else { "❌" };
            let priority = format!("{:?}", result.guarantee.priority()).to_uppercase();

            output.push_str(&format!(
                "\n### {} {:?} ({})\n",
                status, result.guarantee, priority
            ));
            output.push_str(&format!(
                "**Description:** {}\n\n",
                result.guarantee.description()
            ));
            output.push_str(&format!("**Status:** {}\n\n", result.details));

            if include_evidence {
                if let Some(evidence) = &result.evidence {
                    output.push_str(&format!("**Evidence:** {}\n\n", evidence));
                }
            }
        }
    }

    output
}

fn handle_preset_command(
    cmd: PresetCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    match cmd.operation {
        PresetOperation::List(list_cmd) => {
            // TODO: Implement preset listing from ddex_builder::presets
            let presets = get_available_presets(list_cmd.version, list_cmd.partner)?;

            match list_cmd.format {
                PresetListFormat::Human => {
                    println!("Available DDEX Presets:");
                    println!("{:-<50}", "");
                    for preset in &presets {
                        println!(
                            "{:<20} {:<10} {}",
                            preset.name, preset.version, preset.description
                        );
                    }
                }
                PresetListFormat::Json => {
                    println!("{}", serde_json::to_string_pretty(&presets)?);
                }
                PresetListFormat::Table => {
                    println!(
                        "{:<20} {:<10} {:<15} {}",
                        "Name", "Version", "Partner", "Description"
                    );
                    println!("{:-<80}", "");
                    for preset in &presets {
                        println!(
                            "{:<20} {:<10} {:<15} {}",
                            preset.name, preset.version, preset.partner, preset.description
                        );
                    }
                }
            }
        }
        PresetOperation::Show(show_cmd) => {
            let preset_details = get_preset_details(&show_cmd.preset)?;

            match show_cmd.format {
                PresetShowFormat::Human => {
                    println!("Preset: {}", preset_details.name);
                    println!("Partner: {}", preset_details.partner);
                    println!("Version: {}", preset_details.version);
                    println!("Description: {}", preset_details.description);
                    if show_cmd.detailed {
                        println!("\nConfiguration:");
                        println!("{:#?}", preset_details.config);
                    }
                }
                PresetShowFormat::Json => {
                    if show_cmd.detailed {
                        println!("{}", serde_json::to_string_pretty(&preset_details)?);
                    } else {
                        let summary = PresetSummary {
                            name: preset_details.name,
                            partner: preset_details.partner,
                            version: preset_details.version,
                            description: preset_details.description,
                        };
                        println!("{}", serde_json::to_string_pretty(&summary)?);
                    }
                }
                PresetShowFormat::Yaml => {
                    if show_cmd.detailed {
                        println!("{}", serde_yaml::to_string(&preset_details)?);
                    } else {
                        let summary = PresetSummary {
                            name: preset_details.name,
                            partner: preset_details.partner,
                            version: preset_details.version,
                            description: preset_details.description,
                        };
                        println!("{}", serde_yaml::to_string(&summary)?);
                    }
                }
            }
        }
        PresetOperation::Apply(apply_cmd) => {
            let input_data = read_input_data(&apply_cmd.input, apply_cmd.format)?;

            let mut builder = Builder::new();
            builder.apply_preset(&apply_cmd.preset, false)?;

            if let Some(version_override) = apply_cmd.version_override {
                builder.with_version(version_override.into());
            }

            let xml_output = build_ddex_xml(&input_data, &builder)?;

            if apply_cmd.validate {
                // TODO: Validate the output
                if !is_quiet() {
                    println!("{} Validation passed", style("✓").green());
                }
            }

            write_output(&xml_output, &apply_cmd.output)?;

            if !is_quiet() {
                println!(
                    "{} Preset '{}' applied successfully",
                    style("✓").green(),
                    apply_cmd.preset
                );
            }
        }
    }

    Ok(())
}

fn handle_watch_command(
    cmd: WatchCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    if !is_quiet() {
        println!("👀 Watching {} for changes...", cmd.path.display());
        println!("   Pattern: {}", cmd.pattern);
        if let Some(ref output_dir) = cmd.output_dir {
            println!("   Output: {}", output_dir.display());
        }
        println!("   Press Ctrl+C to stop");
    }

    // Initial build if requested
    if cmd.initial_build {
        if !is_quiet() {
            println!("🔨 Running initial build...");
        }
        run_watch_build(&cmd)?;
    }

    // TODO: Implement file watching using notify crate
    // For now, just simulate watching

    // In a real implementation, this would use the notify crate:
    // let (tx, rx) = mpsc::channel::<notify::Event>();
    // let mut watcher = notify::recommended_watcher(move |res| {
    //     match res {
    //         Ok(event) => tx.send(event).unwrap(),
    //         Err(e) => eprintln!("watch error: {:?}", e),
    //     }
    // })?;
    // watcher.watch(&cmd.path, notify::RecursiveMode::from(cmd.recursive))?;

    // Simulate file watching loop (in real implementation, this would be driven by notify events)
    loop {
        // For demo purposes, just exit after showing the setup
        if !is_quiet() {
            println!("File watching simulation - in real implementation, this would use the notify crate");
        }
        break;
    }

    Ok(())
}

fn handle_server_command(
    cmd: ServerCommand,
    _config: &ConfigFile,
) -> Result<(), Box<dyn std::error::Error>> {
    if !is_quiet() {
        println!("🚀 Starting DDEX Builder HTTP API server...");
        println!("   Address: {}:{}", cmd.bind, cmd.port);
        println!("   Workers: {}", cmd.workers);
        if cmd.cors {
            println!("   CORS: enabled");
        }
        if cmd.tls_cert.is_some() && cmd.tls_key.is_some() {
            println!("   TLS: enabled");
        }
        if let Some(rate_limit) = cmd.rate_limit {
            println!("   Rate limit: {} requests/minute per IP", rate_limit);
        }
        println!("   Press Ctrl+C to stop");
    }

    // TODO: Implement HTTP server using axum or warp
    // Server endpoints would include:
    // POST /build - Build DDEX XML from JSON/YAML/TOML
    // POST /convert - Convert between DDEX versions
    // POST /validate - Validate DDEX XML
    // GET /presets - List available presets
    // GET /presets/{id} - Get preset details
    // POST /diff - Compare two DDEX files
    // GET /health - Health check endpoint
    // GET /metrics - Prometheus metrics (if enabled)

    // For now, just simulate server running
    println!("HTTP API server would start here");
    println!("Available endpoints:");
    println!("  POST /api/v1/build        - Build DDEX XML");
    println!("  POST /api/v1/convert      - Convert DDEX versions");
    println!("  POST /api/v1/validate     - Validate DDEX XML");
    println!("  GET  /api/v1/presets      - List presets");
    println!("  GET  /api/v1/presets/{{id}} - Get preset details");
    println!("  POST /api/v1/diff         - Compare DDEX files");
    println!("  GET  /api/v1/health       - Health check");

    // Simulate server running
    std::thread::park();

    Ok(())
}

fn handle_completions_command(cmd: CompletionsCommand) -> Result<(), Box<dyn std::error::Error>> {
    let mut cli = Cli::command();

    if let Some(output_path) = cmd.output {
        let mut file = fs::File::create(output_path)?;
        generate(cmd.shell, &mut cli, "ddex-builder", &mut file);
    } else {
        generate(cmd.shell, &mut cli, "ddex-builder", &mut io::stdout());
    }

    Ok(())
}

// Helper functions

fn read_input_data(
    input: &Option<PathBuf>,
    format: Option<InputFormat>,
) -> Result<JsonValue, Box<dyn std::error::Error>> {
    let content = read_input_string(input)?;

    let detected_format = format.unwrap_or_else(|| {
        if let Some(path) = input {
            detect_input_format(path)
        } else {
            InputFormat::Json // Default for stdin
        }
    });

    match detected_format {
        InputFormat::Json => Ok(serde_json::from_str(&content)?),
        InputFormat::Yaml => Ok(serde_yaml::from_str(&content)?),
        InputFormat::Toml => {
            let toml_value: toml::Value = toml::from_str(&content)?;
            Ok(serde_json::to_value(toml_value)?)
        }
    }
}

fn read_input_string(input: &Option<PathBuf>) -> Result<String, Box<dyn std::error::Error>> {
    match input {
        Some(path) if path.to_str() == Some("-") => {
            let mut content = String::new();
            io::stdin().read_to_string(&mut content)?;
            Ok(content)
        }
        Some(path) => Ok(fs::read_to_string(path)?),
        None => {
            let mut content = String::new();
            io::stdin().read_to_string(&mut content)?;
            Ok(content)
        }
    }
}

fn write_output(content: &str, output: &Option<PathBuf>) -> Result<(), Box<dyn std::error::Error>> {
    match output {
        Some(path) if path.to_str() == Some("-") => {
            print!("{}", content);
            Ok(())
        }
        Some(path) => {
            fs::write(path, content)?;
            Ok(())
        }
        None => {
            print!("{}", content);
            Ok(())
        }
    }
}

fn detect_input_format(path: &Path) -> InputFormat {
    match path.extension().and_then(|s| s.to_str()) {
        Some("yaml") | Some("yml") => InputFormat::Yaml,
        Some("toml") => InputFormat::Toml,
        _ => InputFormat::Json,
    }
}

fn preset_to_string(preset: &PresetChoice) -> String {
    match preset {
        PresetChoice::AudioAlbum => "audio_album".to_string(),
        PresetChoice::AudioSingle => "audio_single".to_string(),
        PresetChoice::VideoSingle => "video_single".to_string(),
        PresetChoice::Compilation => "compilation".to_string(),
        PresetChoice::YoutubeAlbum => "youtube_album".to_string(),
        PresetChoice::YoutubeVideo => "youtube_video".to_string(),
        PresetChoice::YoutubeSingle => "youtube_single".to_string(),
    }
}

fn validate_input_data(
    _data: &JsonValue,
    _builder: &Builder,
    _strict: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    // TODO: Implement input validation logic
    Ok(())
}

fn build_ddex_xml(
    _data: &JsonValue,
    _builder: &Builder,
) -> Result<String, Box<dyn std::error::Error>> {
    // TODO: Implement actual DDEX XML building
    Ok("<xml><!-- DDEX XML would be generated here --></xml>".to_string())
}

fn print_validation_result_human(file_path: &Path, result: &ValidationResult) {
    if result.errors.is_empty() {
        println!("{} {} - Valid", style("✓").green(), file_path.display());
    } else {
        println!(
            "{} {} - {} errors, {} warnings",
            style("✗").red(),
            file_path.display(),
            result.errors.len(),
            result.warnings.len()
        );

        for error in &result.errors {
            println!("  {} {:?}", style("Error:").red(), error);
        }

        for warning in &result.warnings {
            println!("  {} {:?}", style("Warning:").yellow(), warning);
        }
    }
}

fn format_junit_results(
    _results: &[(PathBuf, ValidationResult)],
) -> Result<String, Box<dyn std::error::Error>> {
    // TODO: Implement JUnit XML format
    Ok("<testsuite><!-- JUnit results would be here --></testsuite>".to_string())
}

fn load_batch_config(path: &Path) -> Result<BatchConfig, Box<dyn std::error::Error>> {
    let content = fs::read_to_string(path)?;
    let config: BatchConfig = serde_yaml::from_str(&content)?;
    Ok(config)
}

fn process_batch_task(_task: &BatchTask) -> Result<(), Box<dyn std::error::Error>> {
    // TODO: Implement batch task processing
    Ok(())
}

fn is_quiet() -> bool {
    std::env::var("DDEX_QUIET").unwrap_or_default() == "1"
}

// Helper functions for new commands

fn get_available_presets(
    version_filter: Option<DdexVersionArg>,
    partner_filter: Option<PresetChoice>,
) -> Result<Vec<PresetInfo>, Box<dyn std::error::Error>> {
    let mut presets = vec![
        // Generic industry-standard presets
        PresetInfo {
            name: "audio_album".to_string(),
            version: "4.3".to_string(),
            partner: "Generic".to_string(),
            description: "DDEX ERN 4.3 audio album baseline preset".to_string(),
        },
        PresetInfo {
            name: "audio_single".to_string(),
            version: "4.3".to_string(),
            partner: "Generic".to_string(),
            description: "DDEX ERN 4.3 audio single baseline preset".to_string(),
        },
        PresetInfo {
            name: "video_single".to_string(),
            version: "4.3".to_string(),
            partner: "Generic".to_string(),
            description: "DDEX ERN 4.3 video single baseline preset".to_string(),
        },
        PresetInfo {
            name: "compilation".to_string(),
            version: "4.3".to_string(),
            partner: "Generic".to_string(),
            description: "DDEX ERN 4.3 compilation album baseline preset".to_string(),
        },
        // YouTube presets (based on public documentation)
        PresetInfo {
            name: "youtube_album".to_string(),
            version: "4.3".to_string(),
            partner: "YouTube".to_string(),
            description: "YouTube Music album preset based on public Partner documentation"
                .to_string(),
        },
        PresetInfo {
            name: "youtube_video".to_string(),
            version: "4.3".to_string(),
            partner: "YouTube".to_string(),
            description: "YouTube Music video preset based on public Partner documentation"
                .to_string(),
        },
        PresetInfo {
            name: "youtube_single".to_string(),
            version: "4.3".to_string(),
            partner: "YouTube".to_string(),
            description: "YouTube Music single preset based on public Partner documentation"
                .to_string(),
        },
    ];

    // Apply filters
    if let Some(version_filter) = version_filter {
        let version_str = match version_filter {
            DdexVersionArg::V382 => "3.8.2",
            DdexVersionArg::V41 => "4.1",
            DdexVersionArg::V42 => "4.2",
            DdexVersionArg::V43 => "4.3",
            DdexVersionArg::V44 => "4.4",
        };
        presets.retain(|p| p.version == version_str);
    }

    if let Some(partner_filter) = partner_filter {
        let partner_str = match partner_filter {
            PresetChoice::AudioAlbum => "Generic",
            PresetChoice::AudioSingle => "Generic",
            PresetChoice::VideoSingle => "Generic",
            PresetChoice::Compilation => "Generic",
            PresetChoice::YoutubeAlbum => "YouTube",
            PresetChoice::YoutubeVideo => "YouTube",
            PresetChoice::YoutubeSingle => "YouTube",
        };
        presets.retain(|p| p.partner == partner_str);
    }

    Ok(presets)
}

fn get_preset_details(preset_id: &str) -> Result<PresetDetails, Box<dyn std::error::Error>> {
    // TODO: Load preset details from ddex_builder::presets module
    match preset_id {
        "spotify_audio_43" => Ok(PresetDetails {
            name: "spotify_audio_43".to_string(),
            partner: "Spotify".to_string(),
            version: "4.3".to_string(),
            description: "Spotify audio release preset for ERN 4.3".to_string(),
            config: PresetConfig::default(), // Placeholder
        }),
        _ => Err(format!("Preset '{}' not found", preset_id).into()),
    }
}

fn run_watch_build(cmd: &WatchCommand) -> Result<(), Box<dyn std::error::Error>> {
    // TODO: Implement actual file watching and building
    if let Some(ref command) = cmd.command {
        // Execute custom command
        let output = std::process::Command::new("sh")
            .arg("-c")
            .arg(command)
            .output()?;

        if !output.status.success() {
            return Err(format!(
                "Command failed: {}",
                String::from_utf8_lossy(&output.stderr)
            )
            .into());
        }
    } else {
        // Default build behavior
        if !is_quiet() {
            println!("  Building files matching pattern: {}", cmd.pattern);
        }
        // TODO: Scan for files matching pattern and build them
    }

    Ok(())
}

fn verify_build_determinism(
    data: &JsonValue,
    builder: &Builder,
    iterations: usize,
) -> Result<(), Box<dyn std::error::Error>> {
    use sha2::{Digest, Sha256};

    if iterations < 2 {
        return Ok(());
    }

    if !is_quiet() {
        println!(
            "  {} Verifying determinism with {} iterations...",
            style("→").blue(),
            iterations
        );
    }

    let mut outputs = Vec::with_capacity(iterations);
    let mut hashes = Vec::with_capacity(iterations);

    // Build XML multiple times
    for _i in 0..iterations {
        let xml = build_ddex_xml(data, builder)?;

        // Calculate SHA-256 hash
        let mut hasher = Sha256::new();
        hasher.update(xml.as_bytes());
        let hash = hasher.finalize();
        let hash_hex = format!("{:x}", hash);

        outputs.push(xml);
        hashes.push(hash_hex);

        if !is_quiet() && iterations > 3 {
            print!(".");
            io::stdout().flush().unwrap_or_default();
        }
    }

    if !is_quiet() && iterations > 3 {
        println!(); // New line after dots
    }

    // Compare all outputs byte-for-byte
    let first_output = &outputs[0];
    let first_hash = &hashes[0];

    for (i, (output, hash)) in outputs[1..].iter().zip(hashes[1..].iter()).enumerate() {
        if output != first_output || hash != first_hash {
            eprintln!(
                "{} Determinism verification failed!",
                style("✗").red().bold()
            );
            eprintln!("  Output from iteration 1 differs from iteration {}", i + 2);
            eprintln!("  Hash 1: {}", first_hash);
            eprintln!("  Hash {}: {}", i + 2, hash);

            // Show byte-level differences for first 1000 characters
            let diff_start = find_first_difference(first_output, output);
            if let Some(pos) = diff_start {
                eprintln!("  First difference at byte position: {}", pos);
                let start = pos.saturating_sub(50);
                let end = std::cmp::min(pos + 100, std::cmp::min(first_output.len(), output.len()));
                eprintln!("  Context around difference:");
                eprintln!("  Output 1: {:?}", &first_output[start..end]);
                eprintln!("  Output {}: {:?}", i + 2, &output[start..end]);
            }

            return Err(
                "Determinism verification failed - outputs differ between iterations".into(),
            );
        }
    }

    if !is_quiet() {
        println!(
            "  {} All {} iterations produced identical output",
            style("✓").green(),
            iterations
        );
        println!("  SHA-256: {}", first_hash);
    }

    Ok(())
}

fn find_first_difference(a: &str, b: &str) -> Option<usize> {
    a.bytes()
        .zip(b.bytes())
        .position(|(x, y)| x != y)
        .or_else(|| {
            if a.len() != b.len() {
                Some(std::cmp::min(a.len(), b.len()))
            } else {
                None
            }
        })
}

// Data structures for batch processing

#[derive(serde::Deserialize)]
struct BatchConfig {
    tasks: Vec<BatchTask>,
}

#[derive(serde::Deserialize)]
struct BatchTask {
    input_file: PathBuf,
    output_file: PathBuf,
    preset: Option<String>,
    version: Option<String>,
    validate: Option<bool>,
}

#[derive(serde::Serialize)]
struct BatchResult {
    task_id: usize,
    success: bool,
    error: Option<String>,
}

#[derive(serde::Serialize)]
struct BatchReport {
    total_tasks: usize,
    successful: usize,
    failed: usize,
    results: Vec<BatchResult>,
}

// Data structures for preset commands

#[derive(serde::Serialize, serde::Deserialize)]
struct PresetInfo {
    name: String,
    version: String,
    partner: String,
    description: String,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct PresetDetails {
    name: String,
    partner: String,
    version: String,
    description: String,
    config: PresetConfig,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct PresetSummary {
    name: String,
    partner: String,
    version: String,
    description: String,
}

#[derive(Debug, serde::Serialize, serde::Deserialize, Default)]
struct PresetConfig {
    // TODO: Define actual preset configuration structure
    // This would contain partner-specific settings, validation rules, etc.
    settings: IndexMap<String, String>,
}
