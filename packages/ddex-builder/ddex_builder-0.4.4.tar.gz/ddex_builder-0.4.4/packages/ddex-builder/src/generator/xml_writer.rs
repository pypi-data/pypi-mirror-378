//! XML serialization from AST

use crate::ast::{Element, Node, AST};
use crate::determinism::{DeterminismConfig, IndentChar};
use crate::error::BuildError;
use ddex_core::models::CommentPosition; // Fixed import
use indexmap::IndexMap;
use std::io::Write;

/// XML Writer for converting AST to XML string
pub struct XmlWriter {
    config: DeterminismConfig,
}

impl XmlWriter {
    /// Create a new XML writer
    pub fn new(config: DeterminismConfig) -> Self {
        Self { config }
    }

    /// Write AST to XML string
    pub fn write(&self, ast: &AST) -> Result<String, BuildError> {
        let mut buffer = Vec::new();

        // Write XML declaration
        writeln!(&mut buffer, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")?;

        // Write root element with namespaces
        self.write_element(
            &mut buffer,
            &ast.root,
            &ast.namespaces,
            ast.schema_location.as_deref(),
            0,
        )?;

        Ok(String::from_utf8(buffer).map_err(|e| BuildError::Serialization(e.to_string()))?)
    }

    fn write_element(
        &self,
        writer: &mut impl Write,
        element: &Element,
        namespaces: &IndexMap<String, String>,
        schema_location: Option<&str>,
        depth: usize,
    ) -> Result<(), BuildError> {
        let indent = self.get_indent(depth);

        // Start tag
        write!(writer, "{}<", indent)?;

        // Add namespace prefix if needed
        let element_name = if let Some(ns) = &element.namespace {
            format!("{}:{}", ns, element.name)
        } else if depth == 0 && !namespaces.is_empty() {
            // Root element gets default namespace prefix if available
            if let Some((prefix, _)) = namespaces.first() {
                format!("{}:{}", prefix, element.name)
            } else {
                element.name.clone()
            }
        } else {
            element.name.clone()
        };

        write!(writer, "{}", element_name)?;

        // Add namespace declarations on root element
        if depth == 0 {
            for (prefix, uri) in namespaces {
                write!(writer, " xmlns:{}=\"{}\"", prefix, uri)?;
            }

            if let Some(location) = schema_location {
                write!(writer, " xsi:schemaLocation=\"{}\"", location)?;
            }
        }

        // Add attributes (in deterministic order)
        for (key, value) in &element.attributes {
            write!(writer, " {}=\"{}\"", key, self.escape_attribute(value))?;
        }

        // Check if we have children
        if element.children.is_empty() {
            writeln!(writer, "/>")?;
        } else {
            // Check if we only have text content
            let only_text =
                element.children.len() == 1 && matches!(&element.children[0], Node::Text(_));

            if only_text {
                // Inline text content
                write!(writer, ">")?;
                if let Node::Text(text) = &element.children[0] {
                    write!(writer, "{}", self.escape_text(text))?;
                }
                writeln!(writer, "</{}>", element_name)?;
            } else {
                // Has child elements
                writeln!(writer, ">")?;

                // Write children
                for child in &element.children {
                    match child {
                        Node::Element(child_elem) => {
                            self.write_element(writer, child_elem, namespaces, None, depth + 1)?;
                        }
                        Node::Text(text) => {
                            let child_indent = self.get_indent(depth + 1);
                            writeln!(writer, "{}{}", child_indent, self.escape_text(text))?;
                        }
                        Node::Comment(comment) => {
                            self.write_comment(writer, comment, depth + 1)?;
                        }
                        Node::SimpleComment(comment) => {
                            let child_indent = self.get_indent(depth + 1);
                            writeln!(writer, "{}<!-- {} -->", child_indent, comment)?;
                        }
                    }
                }

                // Close tag
                writeln!(writer, "{}</{}>", indent, element_name)?;
            }
        }

        Ok(())
    }

    fn get_indent(&self, depth: usize) -> String {
        let indent_char = match self.config.indent_char {
            IndentChar::Space => " ", // Fixed: removed super::determinism::
            IndentChar::Tab => "\t",  // Fixed: removed super::determinism::
        };
        indent_char.repeat(depth * self.config.indent_width)
    }

    fn escape_text(&self, text: &str) -> String {
        text.replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
    }

    fn escape_attribute(&self, text: &str) -> String {
        text.replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
            .replace('"', "&quot;")
            .replace('\'', "&apos;")
    }

    /// Write a structured comment with position-aware formatting
    fn write_comment(
        &self,
        writer: &mut impl Write,
        comment: &ddex_core::models::Comment,
        depth: usize,
    ) -> Result<(), BuildError> {
        let indent = match comment.position {
            CommentPosition::Before | CommentPosition::After => {
                // Comments at element level use element indentation
                self.get_indent(depth.saturating_sub(1))
            }
            CommentPosition::FirstChild | CommentPosition::LastChild => {
                // Comments inside elements use child indentation
                self.get_indent(depth)
            }
            CommentPosition::Inline => {
                // Inline comments don't get indentation
                String::new()
            }
        };

        // Use the comment's XML formatting which handles escaping
        let comment_xml = comment.to_xml();
        writeln!(writer, "{}{}", indent, comment_xml)?;

        Ok(())
    }
}

// Removed duplicate From<std::io::Error> implementation
// (it's already in error.rs)
