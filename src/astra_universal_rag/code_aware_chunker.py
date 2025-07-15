#!/usr/bin/env python3
"""
Code-Aware Chunker for Claude Code RAG Enhancement
Intelligently chunks code while preserving logical units and context
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import re
import ast
import json
import logging
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class ChunkType(Enum):
    """Types of chunks for better categorization"""

    FUNCTION = "function"
    CLASS = "class"
    IMPORT_BLOCK = "import_block"
    DOCUMENTATION = "documentation"
    CONFIG = "config"
    API_DEFINITION = "api_definition"
    TEST = "test"
    SCHEMA = "schema"
    TEMPLATE = "template"
    COMBINED = "combined"
    GENERIC = "generic"


class DocumentTemplate(ABC):
    """Abstract base class for document templates - RAGFlow inspired"""

    @abstractmethod
    def detect(self, content: str, file_path: str) -> bool:
        """Detect if this template applies to the document"""
        pass

    @abstractmethod
    def chunk(self, content: str, file_path: str) -> List["CodeChunk"]:
        """Apply template-specific chunking"""
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Get template priority (higher = more specific)"""
        pass


@dataclass
class CodeChunk:
    """Represents a semantically meaningful chunk of code with template awareness"""

    content: str
    metadata: Dict[str, Any]
    start_line: int
    end_line: int
    chunk_type: ChunkType
    language: str
    importance: str = "medium"  # 'critical', 'high', 'medium', 'low'
    template_applied: Optional[str] = None  # Which template was used
    quality_score: float = 0.0  # RAGFlow inspired quality scoring


class CodeAwareChunker:
    """Intelligently chunks code with template-based chunking - RAGFlow inspired"""

    def __init__(self, config: Dict[str, Any]):
        self.max_chunk_size = config.get("claude_context_size", 8000)
        self.standard_chunk_size = config.get("chunk_size", 4000)
        self.chunk_overlap = config.get("chunk_overlap", 800)
        self.language_patterns = self._build_language_patterns()
        self.templates = self._initialize_templates()
        self.quality_threshold = config.get("quality_threshold", 0.7)

    def chunk_file(self, file_path: str, content: str) -> List[CodeChunk]:
        """Chunk a file using template-based intelligent chunking"""
        file_ext = Path(file_path).suffix.lstrip(".")
        _ = Path(file_path).name  # Fixed F841

        # Determine file language and type
        language = self._detect_language(file_ext, content)

        # Try template-based chunking first (RAGFlow inspired)
        template_chunks = self._apply_template_chunking(content, file_path, language)
        if template_chunks:
            return self._assess_chunk_quality(template_chunks)

        # Fallback to language-specific chunking
        if language == "python":
            chunks = self._chunk_python(content, file_path)
        elif language == "dart":
            chunks = self._chunk_dart(content, file_path)
        elif language == "cairo":
            chunks = self._chunk_cairo(content, file_path)
        elif language == "markdown":
            chunks = self._chunk_markdown(content, file_path)
        elif language in ["json", "yaml", "toml"]:
            chunks = self._chunk_config(content, file_path, language)
        else:
            chunks = self._chunk_generic(content, file_path, language)

        return self._assess_chunk_quality(chunks)

    def _detect_language(self, file_ext: str, content: str) -> str:
        """Detect programming language from file extension and content"""
        ext_map = {
            "py": "python",
            "dart": "dart",
            "cairo": "cairo",
            "md": "markdown",
            "json": "json",
            "yaml": "yaml",
            "yml": "yaml",
            "toml": "toml",
            "sh": "bash",
            "rs": "rust",
            "js": "javascript",
            "ts": "typescript",
        }

        return ext_map.get(file_ext, "text")

    def _chunk_python(self, content: str, file_path: str) -> List[CodeChunk]:
        """Python-specific intelligent chunking using AST"""
        chunks = []

        try:
            tree = ast.parse(content)
            lines = content.split("\n")

            # Extract imports as a unified chunk
            imports = self._extract_python_imports(tree, lines)
            if imports:
                chunks.append(
                    CodeChunk(
                        content=imports,
                        metadata={
                            "file_path": file_path,
                            "language": "python",
                            "chunk_type": "imports",
                            "description": "Import statements and dependencies",
                        },
                        start_line=1,
                        end_line=len(imports.split("\n")),
                        chunk_type=ChunkType.IMPORT_BLOCK,
                        language="python",
                        importance="high",
                    )
                )

            # Extract module-level docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                chunks.append(
                    CodeChunk(
                        content=f'"""\n{module_docstring}\n"""',
                        metadata={
                            "file_path": file_path,
                            "language": "python",
                            "chunk_type": "module_documentation",
                            "description": "Module-level documentation",
                        },
                        start_line=1,
                        end_line=10,  # Approximate
                        chunk_type=ChunkType.DOCUMENTATION,
                        language="python",
                        importance="high",
                    )
                )

            # Extract classes with their methods (complete class definitions)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_chunk = self._extract_python_class(node, lines, file_path)
                    if class_chunk:
                        chunks.append(class_chunk)

            # Extract standalone functions (not inside classes)
            for node in tree.body:  # Only top-level nodes
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_chunk = self._extract_python_function(node, lines, file_path)
                    if func_chunk:
                        chunks.append(func_chunk)

        except SyntaxError as e:
            # Fallback to pattern-based chunking for invalid Python
            logger.warning(f"Python AST parsing failed for {file_path}: {e}")
            return self._chunk_by_patterns(content, file_path, "python")

        # If no logical chunks found, fall back to size-based
        if not chunks:
            return self._chunk_by_size(content, file_path, "python")

        return chunks

    def _extract_python_imports(self, tree: ast.AST, lines: List[str]) -> str:
        """Extract all import statements"""
        import_lines = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, "lineno"):
                    # Get the actual line text
                    line_idx = node.lineno - 1
                    if line_idx < len(lines):
                        import_lines.append(lines[line_idx])

        return "\n".join(import_lines) if import_lines else ""

    def _extract_python_class(
        self, node: ast.ClassDef, lines: List[str], file_path: str
    ) -> Optional[CodeChunk]:
        """Extract a Python class with its methods and docstring"""
        try:
            start_line = node.lineno
            end_line = (
                node.end_lineno if hasattr(node, "end_lineno") else start_line + 50
            )

            # Get class content
            class_lines = lines[start_line - 1 : end_line]
            content = "\n".join(class_lines)

            # Limit size
            if len(content) > self.max_chunk_size:
                content = content[: self.max_chunk_size] + "\n# ... (truncated)"

            # Extract class docstring
            docstring = ast.get_docstring(node)
            description = f"Class {node.name}"
            if docstring:
                description += f": {docstring.split('.')[0]}"

            return CodeChunk(
                content=content,
                metadata={
                    "file_path": file_path,
                    "language": "python",
                    "class_name": node.name,
                    "type": "class",
                    "methods": [
                        method.name
                        for method in node.body
                        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ],
                    "description": description,
                },
                start_line=start_line,
                end_line=end_line,
                chunk_type=ChunkType.CLASS,
                language="python",
                importance="high",
            )
        except Exception:
            return None

    def _extract_python_function(
        self, node: ast.FunctionDef, lines: List[str], file_path: str
    ) -> Optional[CodeChunk]:
        """Extract a Python function with its docstring"""
        try:
            start_line = node.lineno
            end_line = (
                node.end_lineno if hasattr(node, "end_lineno") else start_line + 20
            )

            # Get function content
            func_lines = lines[start_line - 1 : end_line]
            content = "\n".join(func_lines)

            # Limit size
            if len(content) > self.standard_chunk_size:
                content = content[: self.standard_chunk_size] + "\n# ... (truncated)"

            # Extract function docstring
            docstring = ast.get_docstring(node)
            description = f"Function {node.name}"
            if docstring:
                description += f": {docstring.split('.')[0]}"

            return CodeChunk(
                content=content,
                metadata={
                    "file_path": file_path,
                    "language": "python",
                    "function_name": node.name,
                    "type": "function",
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "args": [arg.arg for arg in node.args.args],
                    "description": description,
                },
                start_line=start_line,
                end_line=end_line,
                chunk_type=ChunkType.FUNCTION,
                language="python",
                importance="medium",
            )
        except Exception:
            return None

    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is a method inside a class"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False

    def _chunk_dart(self, content: str, file_path: str) -> List[CodeChunk]:
        """Dart-specific intelligent chunking"""
        chunks = []
        lines = content.split("\n")

        # Extract imports
        import_pattern = r"^import\s+[\'\"][^\'\"]*.dart[\'\"]\s*;?$"
        export_pattern = r"^export\s+[\'\"][^\'\"]*.dart[\'\"]\s*;?$"

        import_lines = []
        for i, line in enumerate(lines):
            if re.match(import_pattern, line.strip()) or re.match(
                export_pattern, line.strip()
            ):
                import_lines.append(line)

        if import_lines:
            chunks.append(
                CodeChunk(
                    content="\n".join(import_lines),
                    metadata={
                        "file_path": file_path,
                        "language": "dart",
                        "chunk_type": "imports",
                        "description": "Import and export statements",
                    },
                    start_line=1,
                    end_line=len(import_lines),
                    chunk_type=ChunkType.IMPORT_BLOCK,
                    language="dart",
                    importance="high",
                )
            )

        # Extract classes using regex (since Dart AST parsing is complex)
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}"

        for match in re.finditer(class_pattern, content, re.DOTALL):
            class_name = match.group(1)
            class_content = match.group(0)

            if len(class_content) <= self.max_chunk_size:
                start_line = content[: match.start()].count("\n") + 1
                end_line = content[: match.end()].count("\n") + 1

                chunks.append(
                    CodeChunk(
                        content=class_content,
                        metadata={
                            "file_path": file_path,
                            "language": "dart",
                            "class_name": class_name,
                            "type": "class",
                            "description": f"Dart class {class_name}",
                        },
                        start_line=start_line,
                        end_line=end_line,
                        chunk_type=ChunkType.CLASS,
                        language="dart",
                        importance="high",
                    )
                )

        # Extract standalone functions
        function_pattern = r"(?:static\s+)?(?:Future<[^>]+>\s+|void\s+|\w+\s+)(\w+)\s*\([^)]*\)\s*(?:async\s*)?{[^{}]*(?:{[^{}]*}[^{}]*)*}"

        for match in re.finditer(function_pattern, content, re.DOTALL):
            func_name = match.group(1)
            func_content = match.group(0)

            if len(func_content) <= self.standard_chunk_size:
                start_line = content[: match.start()].count("\n") + 1
                end_line = content[: match.end()].count("\n") + 1

                chunks.append(
                    CodeChunk(
                        content=func_content,
                        metadata={
                            "file_path": file_path,
                            "language": "dart",
                            "function_name": func_name,
                            "type": "function",
                            "description": f"Dart function {func_name}",
                        },
                        start_line=start_line,
                        end_line=end_line,
                        chunk_type=ChunkType.FUNCTION,
                        language="dart",
                        importance="medium",
                    )
                )

        # If no chunks found, fall back to size-based
        if not chunks:
            return self._chunk_by_size(content, file_path, "dart")

        return chunks

    def _chunk_cairo(self, content: str, file_path: str) -> List[CodeChunk]:
        """Cairo-specific intelligent chunking"""
        chunks = []
        lines = content.split("\n")

        # Extract use statements
        use_pattern = r"^use\s+[^;]+;"
        use_lines = []

        for line in lines:
            if re.match(use_pattern, line.strip()):
                use_lines.append(line)

        if use_lines:
            chunks.append(
                CodeChunk(
                    content="\n".join(use_lines),
                    metadata={
                        "file_path": file_path,
                        "language": "cairo",
                        "chunk_type": "imports",
                        "description": "Use statements and dependencies",
                    },
                    start_line=1,
                    end_line=len(use_lines),
                    chunk_type=ChunkType.IMPORT_BLOCK,
                    language="cairo",
                    importance="high",
                )
            )

        # Extract contracts/interfaces
        contract_pattern = (
            r"#\[starknet::contract\]\s*mod\s+(\w+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}"
        )
        interface_pattern = (
            r"#\[starknet::interface\]\s*trait\s+(\w+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}"
        )

        for pattern, chunk_type in [
            (contract_pattern, "contract"),
            (interface_pattern, "interface"),
        ]:
            for match in re.finditer(pattern, content, re.DOTALL):
                name = match.group(1)
                full_content = match.group(0)

                if len(full_content) <= self.max_chunk_size:
                    start_line = content[: match.start()].count("\n") + 1
                    end_line = content[: match.end()].count("\n") + 1

                    chunks.append(
                        CodeChunk(
                            content=full_content,
                            metadata={
                                "file_path": file_path,
                                "language": "cairo",
                                "name": name,
                                "type": chunk_type,
                                "description": f"Cairo {chunk_type} {name}",
                            },
                            start_line=start_line,
                            end_line=end_line,
                            chunk_type=chunk_type,
                            language="cairo",
                            importance="critical",
                        )
                    )

        # Extract functions
        fn_pattern = (
            r"fn\s+(\w+)\s*\([^)]*\)\s*(?:->[^{]+)?\s*{[^{}]*(?:{[^{}]*}[^{}]*)*}"
        )

        for match in re.finditer(fn_pattern, content, re.DOTALL):
            func_name = match.group(1)
            func_content = match.group(0)

            if len(func_content) <= self.standard_chunk_size:
                start_line = content[: match.start()].count("\n") + 1
                end_line = content[: match.end()].count("\n") + 1

                chunks.append(
                    CodeChunk(
                        content=func_content,
                        metadata={
                            "file_path": file_path,
                            "language": "cairo",
                            "function_name": func_name,
                            "type": "function",
                            "description": f"Cairo function {func_name}",
                        },
                        start_line=start_line,
                        end_line=end_line,
                        chunk_type=ChunkType.FUNCTION,
                        language="cairo",
                        importance="high",
                    )
                )

        if not chunks:
            return self._chunk_by_size(content, file_path, "cairo")

        return chunks

    def _chunk_markdown(self, content: str, file_path: str) -> List[CodeChunk]:
        """Markdown-specific intelligent chunking by headers using regex"""
        chunks = []
        lines = content.split("\n")

        # Split by headers (both # and underline styles)
        current_section = []
        current_header = None
        header_level = 0
        section_start_line = 1

        for i, line in enumerate(lines):
            # Check for ATX headers (# ## ###)
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())

            # Check for Setext headers (underlined with = or -)
            setext_match = None
            if i > 0 and not header_match:
                prev_line = lines[i - 1].strip()
                if prev_line and re.match(r"^=+$", line.strip()):
                    setext_match = (1, prev_line)  # H1 equivalent
                elif prev_line and re.match(r"^-+$", line.strip()):
                    setext_match = (2, prev_line)  # H2 equivalent

            if header_match or setext_match:
                # Save previous section
                if current_section and current_header:
                    section_content = "\n".join(current_section)
                    if len(section_content.strip()) > 0:
                        chunks.append(
                            CodeChunk(
                                content=section_content,
                                metadata={
                                    "file_path": file_path,
                                    "language": "markdown",
                                    "section_title": current_header,
                                    "header_level": header_level,
                                    "type": "section",
                                    "description": f"Documentation section: {current_header}",
                                },
                                start_line=section_start_line,
                                end_line=i,
                                chunk_type=ChunkType.DOCUMENTATION,
                                language="markdown",
                                importance=self._get_header_importance(header_level),
                            )
                        )

                # Start new section
                if header_match:
                    header_level = len(header_match.group(1))
                    current_header = header_match.group(2)
                    current_section = [line]
                else:  # setext_match
                    header_level = setext_match[0]
                    current_header = setext_match[1]
                    # Include the previous line and underline
                    current_section = [lines[i - 1], line]

                section_start_line = i + 1
            else:
                current_section.append(line)

        # Add final section
        if current_section and current_header:
            section_content = "\n".join(current_section)
            if len(section_content.strip()) > 0:
                chunks.append(
                    CodeChunk(
                        content=section_content,
                        metadata={
                            "file_path": file_path,
                            "language": "markdown",
                            "section_title": current_header,
                            "header_level": header_level,
                            "type": "section",
                            "description": f"Documentation section: {current_header}",
                        },
                        start_line=section_start_line,
                        end_line=len(lines),
                        chunk_type=ChunkType.DOCUMENTATION,
                        language="markdown",
                        importance=self._get_header_importance(header_level),
                    )
                )

        # If no headers found, check for content and create a single chunk
        if not chunks and content.strip():
            chunks.append(
                CodeChunk(
                    content=content,
                    metadata={
                        "file_path": file_path,
                        "language": "markdown",
                        "section_title": "Content",
                        "header_level": 0,
                        "type": "content",
                        "description": "Markdown content without headers",
                    },
                    start_line=1,
                    end_line=len(lines),
                    chunk_type=ChunkType.DOCUMENTATION,
                    language="markdown",
                    importance="medium",
                )
            )

        return chunks if chunks else self._chunk_by_size(content, file_path, "markdown")

    def _get_header_importance(self, header_level: int) -> str:
        """Determine importance based on header level"""
        if header_level == 1:
            return "high"
        elif header_level == 2:
            return "high"
        elif header_level == 3:
            return "medium"
        else:
            return "low"

    def _chunk_config(
        self, content: str, file_path: str, language: str
    ) -> List[CodeChunk]:
        """Configuration file chunking (JSON, YAML, TOML)"""
        try:
            if language == "json":
                # For JSON, parse and chunk by top-level keys
                data = json.loads(content)
                chunks = []

                for key, value in data.items():
                    chunk_content = f'"{key}": {json.dumps(value, indent=2)}'
                    chunks.append(
                        CodeChunk(
                            content=chunk_content,
                            metadata={
                                "file_path": file_path,
                                "language": language,
                                "config_key": key,
                                "type": "config_section",
                                "description": f"Configuration: {key}",
                            },
                            start_line=1,
                            end_line=len(chunk_content.split("\n")),
                            chunk_type=ChunkType.CONFIG,
                            language=language,
                            importance="medium",
                        )
                    )

                return chunks
        except Exception:  # Fixed E722
            pass

        # Fallback to size-based chunking
        return self._chunk_by_size(content, file_path, language)

    def _chunk_by_size(
        self, content: str, file_path: str, language: str
    ) -> List[CodeChunk]:
        """Fallback size-based chunking with overlap"""
        chunks = []
        lines = content.split("\n")

        chunk_size_lines = self.standard_chunk_size // 80  # Estimate 80 chars per line
        overlap_lines = self.chunk_overlap // 80

        for i in range(0, len(lines), chunk_size_lines - overlap_lines):
            chunk_lines = lines[i : i + chunk_size_lines]
            chunk_content = "\n".join(chunk_lines)

            if chunk_content.strip():
                chunks.append(
                    CodeChunk(
                        content=chunk_content,
                        metadata={
                            "file_path": file_path,
                            "language": language,
                            "type": "text_chunk",
                            "chunk_index": len(chunks),
                            "description": f"{language} code segment",
                        },
                        start_line=i + 1,
                        end_line=min(i + chunk_size_lines, len(lines)),
                        chunk_type=ChunkType.GENERIC,
                        language=language,
                        importance="low",
                    )
                )

        return chunks

    def _chunk_by_patterns(
        self, content: str, file_path: str, language: str
    ) -> List[CodeChunk]:
        """Pattern-based chunking for complex files"""
        # This is a simplified fallback - could be expanded with more patterns
        return self._chunk_by_size(content, file_path, language)

    def _build_language_patterns(self) -> Dict[str, Dict[str, str]]:
        """Build regex patterns for different languages"""
        return {
            "python": {
                "class": r"class\s+(\w+).*?:",
                "function": r"def\s+(\w+)\s*\(",
                "import": r"(?:from\s+\S+\s+)?import\s+.+",
            },
            "dart": {
                "class": r"class\s+(\w+)",
                "function": r"(?:static\s+)?(?:\w+\s+)?(\w+)\s*\(",
                "import": r"import\s+[\'\"][^\'\"]*[\'\"];?",
            },
            "cairo": {
                "contract": r"#\[starknet::contract\]",
                "function": r"fn\s+(\w+)\s*\(",
                "use": r"use\s+[^;]+;",
            },
        }

    def chunk_for_claude_context(
        self, file_path: str, content: str, max_context: int = 8000
    ) -> List[CodeChunk]:
        """Create larger chunks specifically optimized for Claude's context window"""
        standard_chunks = self.chunk_file(file_path, content)

        # Combine related chunks that fit within Claude's context window
        claude_chunks = []
        current_combined = []
        current_size = 0

        for chunk in standard_chunks:
            chunk_size = len(chunk.content)

            if current_size + chunk_size <= max_context and current_combined:
                # Add to current combined chunk
                current_combined.append(chunk)
                current_size += chunk_size
            else:
                # Finalize current combined chunk
                if current_combined:
                    claude_chunks.append(self._create_combined_chunk(current_combined))

                # Start new combined chunk
                current_combined = [chunk]
                current_size = chunk_size

        # Add final combined chunk
        if current_combined:
            claude_chunks.append(self._create_combined_chunk(current_combined))

        return claude_chunks

    def _create_combined_chunk(self, chunks: List[CodeChunk]) -> CodeChunk:
        """Combine multiple chunks into a Claude-optimized chunk"""
        if len(chunks) == 1:
            return chunks[0]

        combined_content = []
        all_metadata = {}
        min_line = min(chunk.start_line for chunk in chunks)
        max_line = max(chunk.end_line for chunk in chunks)

        # Combine content with separators
        for chunk in chunks:
            combined_content.append(
                f"# {chunk.chunk_type.upper()}: {chunk.metadata.get('description', '')}"
            )
            combined_content.append(chunk.content)
            combined_content.append("")  # Empty line separator

            # Merge metadata
            for key, value in chunk.metadata.items():
                if key not in all_metadata:
                    all_metadata[key] = value
                elif isinstance(value, list):
                    if isinstance(all_metadata[key], list):
                        all_metadata[key].extend(value)
                    else:
                        all_metadata[key] = [all_metadata[key]] + value

        all_metadata["combined_chunks"] = len(chunks)
        all_metadata["chunk_types"] = [chunk.chunk_type for chunk in chunks]

        return CodeChunk(
            content="\n".join(combined_content),
            metadata=all_metadata,
            start_line=min_line,
            end_line=max_line,
            chunk_type=ChunkType.COMBINED,
            language=chunks[0].language,
            importance="high",  # Combined chunks are more important
        )

    def _initialize_templates(self) -> List[DocumentTemplate]:
        """Initialize document templates for specialized chunking"""
        return [
            APIDocumentationTemplate(),
            TestFileTemplate(),
            ConfigurationTemplate(),
            RESTAPITemplate(),
            DatabaseSchemaTemplate(),
        ]

    def _apply_template_chunking(
        self, content: str, file_path: str, language: str
    ) -> Optional[List[CodeChunk]]:
        """Apply template-based chunking - RAGFlow inspired"""
        # Sort templates by priority (higher priority first)
        sorted_templates = sorted(
            self.templates, key=lambda t: t.get_priority(), reverse=True
        )

        for template in sorted_templates:
            if template.detect(content, file_path):
                try:
                    chunks = template.chunk(content, file_path)
                    # Mark chunks with template information
                    for chunk in chunks:
                        chunk.template_applied = template.__class__.__name__
                    return chunks
                except Exception as e:
                    # Log error and continue to next template
                    print(f"Template {template.__class__.__name__} failed: {e}")
                    continue

        return None

    def _assess_chunk_quality(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """Assess and score chunk quality - RAGFlow inspired"""
        for chunk in chunks:
            chunk.quality_score = self._calculate_chunk_quality(chunk)

        # Filter out low-quality chunks if threshold is set
        if self.quality_threshold > 0:
            chunks = [
                chunk
                for chunk in chunks
                if chunk.quality_score >= self.quality_threshold
            ]

        return chunks

    def _calculate_chunk_quality(self, chunk: CodeChunk) -> float:
        """Calculate quality score for a chunk"""
        score = 0.0

        # Content length appropriateness (25%)
        content_length = len(chunk.content)
        if 100 <= content_length <= self.max_chunk_size:
            score += 0.25
        elif content_length < 100:
            score += 0.1  # Too short

        # Chunk type specificity (25%)
        if chunk.chunk_type in [
            ChunkType.FUNCTION,
            ChunkType.CLASS,
            ChunkType.API_DEFINITION,
        ]:
            score += 0.25
        elif chunk.chunk_type in [ChunkType.DOCUMENTATION, ChunkType.CONFIG]:
            score += 0.2
        elif chunk.chunk_type == ChunkType.GENERIC:
            score += 0.1

        # Metadata completeness (25%)
        metadata_score = 0
        required_fields = ["file_path", "language", "description"]
        for field in required_fields:
            if chunk.metadata.get(field):
                metadata_score += 1
        score += (metadata_score / len(required_fields)) * 0.25

        # Language-specific quality (25%)
        if chunk.language in ["python", "dart", "cairo"]:
            score += 0.25
        elif chunk.language in ["markdown", "json", "yaml"]:
            score += 0.2
        else:
            score += 0.1

        return min(1.0, score)


# Document Templates - RAGFlow inspired


class APIDocumentationTemplate(DocumentTemplate):
    """Template for API documentation files"""

    def detect(self, content: str, file_path: str) -> bool:
        api_indicators = [
            "API",
            "endpoint",
            "swagger",
            "openapi",
            "rest",
            "graphql",
            "POST",
            "GET",
            "PUT",
            "DELETE",
            "PATCH",
        ]
        content_lower = content.lower()
        return (
            any(indicator.lower() in content_lower for indicator in api_indicators)
            or "api" in file_path.lower()
            or "swagger" in file_path.lower()
        )

    def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        chunks = []

        # Split by API endpoints or major sections
        sections = re.split(r"\n(?=#{1,3}\s)", content)

        for i, section in enumerate(sections):
            if section.strip():
                chunks.append(
                    CodeChunk(
                        content=section,
                        metadata={
                            "file_path": file_path,
                            "language": "markdown",
                            "section_index": i,
                            "description": f"API documentation section {i + 1}",
                        },
                        start_line=1,
                        end_line=len(section.split("\n")),
                        chunk_type=ChunkType.API_DEFINITION,
                        language="markdown",
                        importance="high",
                    )
                )

        return chunks

    def get_priority(self) -> int:
        return 90


class TestFileTemplate(DocumentTemplate):
    """Template for test files"""

    def detect(self, content: str, file_path: str) -> bool:
        return (
            "test" in file_path.lower()
            or "spec" in file_path.lower()
            or "unittest" in content
            or "pytest" in content
            or "describe(" in content
        )

    def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        chunks = []

        # For test files, group by test functions/classes
        test_pattern = r"(def test_\w+|class Test\w+|describe\([^)]+\)|it\([^)]+\))"
        matches = list(re.finditer(test_pattern, content))

        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)

            test_content = content[start_pos:end_pos]
            chunks.append(
                CodeChunk(
                    content=test_content,
                    metadata={
                        "file_path": file_path,
                        "language": "python",
                        "test_name": match.group(1),
                        "description": f"Test case: {match.group(1)}",
                    },
                    start_line=content[:start_pos].count("\n") + 1,
                    end_line=content[:end_pos].count("\n") + 1,
                    chunk_type=ChunkType.TEST,
                    language="python",
                    importance="medium",
                )
            )

        return chunks

    def get_priority(self) -> int:
        return 80


class ConfigurationTemplate(DocumentTemplate):
    """Template for configuration files"""

    def detect(self, content: str, file_path: str) -> bool:
        config_extensions = [".json", ".yaml", ".yml", ".toml", ".env", ".ini"]
        return (
            any(file_path.endswith(ext) for ext in config_extensions)
            or "config" in file_path.lower()
            or "settings" in file_path.lower()
        )

    def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        chunks = []

        try:
            if file_path.endswith(".json"):
                data = json.loads(content)
                for key, value in data.items():
                    chunks.append(
                        CodeChunk(
                            content=f'"{key}": {json.dumps(value, indent=2)}',
                            metadata={
                                "file_path": file_path,
                                "language": "json",
                                "config_key": key,
                                "description": f"Configuration: {key}",
                            },
                            start_line=1,
                            end_line=10,
                            chunk_type=ChunkType.CONFIG,
                            language="json",
                            importance="medium",
                        )
                    )
        except Exception:  # Fixed E722
            # Fallback to simple chunking
            chunks.append(
                CodeChunk(
                    content=content,
                    metadata={
                        "file_path": file_path,
                        "language": "config",
                        "description": "Configuration file",
                    },
                    start_line=1,
                    end_line=len(content.split("\n")),
                    chunk_type=ChunkType.CONFIG,
                    language="config",
                    importance="medium",
                )
            )

        return chunks

    def get_priority(self) -> int:
        return 70


class RESTAPITemplate(DocumentTemplate):
    """Template for REST API definitions"""

    def detect(self, content: str, file_path: str) -> bool:
        return (
            "fastapi" in content.lower()
            or "@app." in content
            or "router" in content.lower()
            or "APIRouter" in content
        )

    def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        chunks = []

        # Find API route definitions
        route_pattern = r"@\w+\.(get|post|put|delete|patch)\(.*?\)\s*\ndef\s+\w+[^:]*:\s*[^\n]*(?:\n(?:\s{4,}[^\n]*)*)*"

        for match in re.finditer(route_pattern, content, re.MULTILINE):
            chunks.append(
                CodeChunk(
                    content=match.group(0),
                    metadata={
                        "file_path": file_path,
                        "language": "python",
                        "api_method": match.group(1).upper(),
                        "description": f"API endpoint: {match.group(1).upper()}",
                    },
                    start_line=content[: match.start()].count("\n") + 1,
                    end_line=content[: match.end()].count("\n") + 1,
                    chunk_type=ChunkType.API_DEFINITION,
                    language="python",
                    importance="high",
                )
            )

        return chunks

    def get_priority(self) -> int:
        return 85


class DatabaseSchemaTemplate(DocumentTemplate):
    """Template for database schema files"""

    def detect(self, content: str, file_path: str) -> bool:
        return (
            "CREATE TABLE" in content.upper()
            or "schema" in file_path.lower()
            or "migration" in file_path.lower()
            or "models.py" in file_path
        )

    def chunk(self, content: str, file_path: str) -> List[CodeChunk]:
        chunks = []

        # Split by table definitions or model classes
        table_pattern = r"(CREATE TABLE\s+\w+|class\s+\w+\([^)]*Model[^)]*\))"

        sections = re.split(table_pattern, content, flags=re.IGNORECASE)

        for i in range(1, len(sections), 2):  # Skip empty sections
            if i + 1 < len(sections):
                table_def = sections[i] + sections[i + 1]
                chunks.append(
                    CodeChunk(
                        content=table_def,
                        metadata={
                            "file_path": file_path,
                            "language": "sql",
                            "table_definition": sections[i],
                            "description": f"Database schema: {sections[i]}",
                        },
                        start_line=1,
                        end_line=len(table_def.split("\n")),
                        chunk_type=ChunkType.SCHEMA,
                        language="sql",
                        importance="high",
                    )
                )

        return chunks

    def get_priority(self) -> int:
        return 75
