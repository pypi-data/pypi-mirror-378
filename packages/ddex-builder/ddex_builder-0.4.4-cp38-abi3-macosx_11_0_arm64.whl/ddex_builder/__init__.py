"""DDEX Builder - High-performance DDEX XML builder with deterministic output."""

__version__ = "0.4.3"

# Try to import the Rust extension
try:
    from ddex_builder._internal import (
        DdexBuilder as _RustDdexBuilder,
        Release as _RustRelease,
        Resource as _RustResource,
        ValidationResult as _RustValidationResult,
        BuilderStats as _RustBuilderStats,
        BuildResult as _RustBuildResult,
        PresetInfo as _RustPresetInfo,
        FidelityOptions as _RustFidelityOptions,
        VerificationResult as _RustVerificationResult,
        ValidationRulePy as _RustValidationRule,
        batch_build as _rust_batch_build,
        validate_structure as _rust_validate_structure,
    )
    _RUST_AVAILABLE = True

    # Use Rust implementations directly
    DdexBuilder = _RustDdexBuilder
    Release = _RustRelease
    Resource = _RustResource
    ValidationResult = _RustValidationResult
    BuilderStats = _RustBuilderStats
    BuildResult = _RustBuildResult
    PresetInfo = _RustPresetInfo
    FidelityOptions = _RustFidelityOptions
    VerificationResult = _RustVerificationResult
    ValidationRule = _RustValidationRule
    batch_build = _rust_batch_build
    validate_structure = _rust_validate_structure

except ImportError as e:
    # Only fall back to mock if truly not available
    _RUST_AVAILABLE = False
    print(f"Warning: Rust extension not available, using mock implementation: {e}")

    # Mock implementations for development only
    class DdexBuilder:
        """Mock DdexBuilder for development/testing."""
        def __init__(self):
            self._releases = []
            self._resources = []

        def add_release(self, release):
            self._releases.append(release)
            return self

        def add_resource(self, resource):
            self._resources.append(resource)
            return self

        def build(self):
            return f"<mock>Built {len(self._releases)} releases</mock>"

        def validate(self):
            return {"valid": True, "errors": []}

        def from_dataframe(self, df):
            return self

        def get_stats(self):
            return {"releases": len(self._releases), "resources": len(self._resources)}

    class Release:
        """Mock Release for development."""
        def __init__(self):
            self.release_id = None
            self.title = None

    class Resource:
        """Mock Resource for development."""
        def __init__(self):
            self.resource_id = None
            self.title = None

    class ValidationResult:
        """Mock ValidationResult for development."""
        pass

    class BuilderStats:
        """Mock BuilderStats for development."""
        pass

    class BuildResult:
        """Mock BuildResult for development."""
        pass

    class PresetInfo:
        """Mock PresetInfo for development."""
        pass

    class FidelityOptions:
        """Mock FidelityOptions for development."""
        pass

    class VerificationResult:
        """Mock VerificationResult for development."""
        pass

    class ValidationRule:
        """Mock ValidationRule for development."""
        pass

    def batch_build(requests):
        """Mock batch_build for development."""
        return [f"<mock>Built from request {i}</mock>" for i, _ in enumerate(requests)]

    def validate_structure(xml):
        """Mock validate_structure for development."""
        return {"valid": True, "errors": [], "warnings": []}

# Public API
__all__ = [
    "__version__",
    "DdexBuilder",
    "Release",
    "Resource",
    "ValidationResult",
    "BuilderStats",
    "BuildResult",
    "PresetInfo",
    "FidelityOptions",
    "VerificationResult",
    "ValidationRule",
    "batch_build",
    "validate_structure",
]

# Helper function to check if using native implementation
def is_rust_available():
    """Check if the native Rust implementation is available."""
    return _RUST_AVAILABLE