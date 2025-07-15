#!/usr/bin/env python3
"""
Predictive Analysis Engine - Phase 3 of God Mode RAG System
Implements predictive developer intent analysis, impact analysis, and pattern recognition
"""

import asyncio
import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from graph_models import knowledge_graph
from rag_system import AstraRAG
from proactive_context_engine import ContextRequest

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Result of predictive analysis"""

    predicted_intent: str
    confidence: float
    next_likely_files: List[str]
    impact_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    analysis_time: float


@dataclass
class ImpactNode:
    """Node in the impact analysis graph"""

    file_path: str
    impact_type: str  # direct, indirect, dependency, caller, test
    impact_strength: float  # 0.0 to 1.0
    reason: str
    distance: int  # degrees of separation from original file


class PredictiveAnalyzer:
    """
    Advanced predictive analysis engine that anticipates developer needs
    and provides impact analysis for changes
    """

    def __init__(self, rag_system: AstraRAG):
        self.rag_system = rag_system
        self.graph = knowledge_graph
        self.prediction_history = []
        self.developer_workflows = {}
        self.file_relationships = {}
        self.change_patterns = {}

        # Pattern recognition models
        self.common_workflows = self._initialize_workflow_patterns()
        self.file_dependency_patterns = self._initialize_dependency_patterns()

        # Configuration
        self.max_impact_depth = 3
        self.min_impact_strength = 0.2
        self.prediction_window = 30  # minutes

    def _initialize_workflow_patterns(self) -> Dict[str, Dict]:
        """Initialize common development workflow patterns"""
        return {
            "model_change_workflow": {
                "pattern": ["model", "service", "controller", "test"],
                "extensions": [".dart", ".py", ".ts"],
                "description": "Data model change typically requires service and UI updates",
            },
            "api_integration_workflow": {
                "pattern": ["api_client", "service", "model", "screen"],
                "extensions": [".dart", ".py"],
                "description": "API changes propagate through service layer to UI",
            },
            "ui_component_workflow": {
                "pattern": ["widget", "screen", "service", "test"],
                "extensions": [".dart"],
                "description": "UI changes often require service updates and tests",
            },
            "database_change_workflow": {
                "pattern": ["migration", "model", "repository", "service"],
                "extensions": [".py", ".sql"],
                "description": "Database changes require model and service layer updates",
            },
        }

    def _initialize_dependency_patterns(self) -> Dict[str, List]:
        """Initialize file dependency patterns based on common architectures"""
        return {
            "flutter_patterns": [
                ("model", ["service", "repository", "screen"]),
                ("service", ["screen", "widget", "test"]),
                ("screen", ["widget", "test"]),
                ("widget", ["test"]),
                ("repository", ["service", "test"]),
            ],
            "python_patterns": [
                ("model", ["service", "api", "test"]),
                ("service", ["api", "test"]),
                ("api", ["test"]),
                ("util", ["service", "api", "test"]),
            ],
        }

    async def analyze_developer_intent(self, request: ContextRequest) -> Dict[str, Any]:
        """
        Main method to predict developer intent and provide proactive insights
        """
        start_time = time.time()

        try:
            # Parallel analysis tasks
            analysis_tasks = [
                self._predict_intent(request),
                self._analyze_impact_radius(request),
                self._predict_next_files(request),
                self._assess_change_risk(request),
                self._generate_recommendations(request),
            ]

            (
                predicted_intent,
                impact_analysis,
                next_files,
                risk_assessment,
                recommendations,
            ) = await asyncio.gather(*analysis_tasks)

            # Calculate overall confidence
            confidence = self._calculate_prediction_confidence(
                predicted_intent, impact_analysis, next_files
            )

            result = {
                "predicted_intent": predicted_intent,
                "confidence": confidence,
                "next_likely_files": next_files,
                "impact_analysis": impact_analysis,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "analysis_time": time.time() - start_time,
                "prediction_timestamp": datetime.now().isoformat(),
            }

            # Store prediction for learning
            await self._store_prediction(request, result)

            return result

        except Exception as e:
            logger.error(f"Error in predictive analysis: {e}")
            return {
                "error": str(e),
                "analysis_time": time.time() - start_time,
                "predicted_intent": "unknown",
                "confidence": 0.0,
            }

    async def _predict_intent(self, request: ContextRequest) -> Dict[str, Any]:
        """Predict developer intent based on context and patterns"""
        try:
            intent_data = {
                "primary_intent": "code_navigation",
                "intent_confidence": 0.5,
                "secondary_intents": [],
                "intent_indicators": [],
            }

            # Analyze file type and naming patterns
            file_path = Path(request.filepath)
            file_name = file_path.stem.lower()
            _ = file_path.suffix.lower()

            # Intent indicators based on file patterns
            intent_indicators = []

            if "test" in file_name or file_name.endswith("_test"):
                intent_data["primary_intent"] = "testing"
                intent_data["intent_confidence"] = 0.8
                intent_indicators.append("File name indicates testing activity")

            elif "model" in file_name or file_name.endswith("_model"):
                intent_data["primary_intent"] = "data_modeling"
                intent_data["intent_confidence"] = 0.7
                intent_indicators.append("File name indicates data model work")

            elif "service" in file_name or file_name.endswith("_service"):
                intent_data["primary_intent"] = "business_logic"
                intent_data["intent_confidence"] = 0.75
                intent_indicators.append(
                    "File name indicates service layer development"
                )

            elif "screen" in file_name or "page" in file_name:
                intent_data["primary_intent"] = "ui_development"
                intent_data["intent_confidence"] = 0.8
                intent_indicators.append("File name indicates UI screen development")

            elif "widget" in file_name or "component" in file_name:
                intent_data["primary_intent"] = "component_development"
                intent_data["intent_confidence"] = 0.75
                intent_indicators.append("File name indicates widget/component work")

            # Analyze function/class focus
            if request.function_name:
                func_name_lower = request.function_name.lower()
                if any(word in func_name_lower for word in ["test", "spec", "should"]):
                    intent_data["secondary_intents"].append("testing")
                    intent_indicators.append(
                        f"Function '{request.function_name}' suggests testing"
                    )

                elif any(
                    word in func_name_lower for word in ["build", "create", "init"]
                ):
                    intent_data["secondary_intents"].append("feature_implementation")
                    intent_indicators.append(
                        f"Function '{request.function_name}' suggests implementation work"
                    )

                elif any(
                    word in func_name_lower for word in ["fix", "resolve", "debug"]
                ):
                    intent_data["secondary_intents"].append("debugging")
                    intent_indicators.append(
                        f"Function '{request.function_name}' suggests debugging"
                    )

            # Analyze recent developer patterns
            dev_pattern = self.developer_workflows.get(request.developer_id, {})
            recent_files = dev_pattern.get("recent_files", [])

            if len(recent_files) >= 2:
                # Look for workflow patterns
                for workflow_name, workflow_data in self.common_workflows.items():
                    if self._matches_workflow_pattern(
                        recent_files + [request.filepath], workflow_data
                    ):
                        intent_data["secondary_intents"].append(
                            f"following_{workflow_name}"
                        )
                        intent_indicators.append(
                            f"File sequence matches {workflow_data['description']}"
                        )
                        intent_data["intent_confidence"] = min(
                            0.9, intent_data["intent_confidence"] + 0.1
                        )

            intent_data["intent_indicators"] = intent_indicators
            return intent_data

        except Exception as e:
            logger.error(f"Error predicting intent: {e}")
            return {
                "error": str(e),
                "primary_intent": "unknown",
                "intent_confidence": 0.0,
            }

    async def _analyze_impact_radius(self, request: ContextRequest) -> Dict[str, Any]:
        """Analyze the blast radius of potential changes to this file"""
        try:
            impact_analysis = {
                "direct_impacts": [],
                "indirect_impacts": [],
                "test_impacts": [],
                "dependency_impacts": [],
                "blast_radius_score": 0.0,
                "critical_paths": [],
            }

            # Find the file in knowledge graph
            target_file = None
            for file_id, file_data in self.graph.nodes.get("files", {}).items():
                if file_data.get("path") == request.filepath:
                    target_file = file_id
                    break

            if not target_file:
                return impact_analysis

            # Analyze direct impacts through commit history
            direct_impacts = await self._find_direct_impacts(target_file)
            impact_analysis["direct_impacts"] = direct_impacts

            # Analyze indirect impacts through file relationships
            indirect_impacts = await self._find_indirect_impacts(request.filepath)
            impact_analysis["indirect_impacts"] = indirect_impacts

            # Find test files that might be affected
            test_impacts = await self._find_test_impacts(request.filepath)
            impact_analysis["test_impacts"] = test_impacts

            # Calculate blast radius score
            total_impacts = (
                len(direct_impacts) + len(indirect_impacts) + len(test_impacts)
            )
            impact_analysis["blast_radius_score"] = min(1.0, total_impacts / 10.0)

            # Identify critical paths
            critical_paths = self._identify_critical_paths(
                direct_impacts + indirect_impacts
            )
            impact_analysis["critical_paths"] = critical_paths

            return impact_analysis

        except Exception as e:
            logger.error(f"Error analyzing impact radius: {e}")
            return {"error": str(e), "blast_radius_score": 0.0}

    async def _find_direct_impacts(self, file_id: str) -> List[Dict[str, Any]]:
        """Find files that are directly related through commits"""
        direct_impacts = []

        try:
            # Find commits that modified this file
            related_commits = set()
            for rel in self.graph.relationships:
                if rel["to"] == file_id and rel["type"] == "MODIFIES":
                    related_commits.add(rel["from"])

            # Find other files modified in the same commits
            for commit_id in list(related_commits)[:5]:  # Limit to recent commits
                for rel in self.graph.relationships:
                    if (
                        rel["from"] == commit_id
                        and rel["type"] == "MODIFIES"
                        and rel["to"] != file_id
                        and rel["to"] in self.graph.nodes.get("files", {})
                    ):
                        related_file = self.graph.nodes["files"][rel["to"]]
                        direct_impacts.append(
                            {
                                "file_path": related_file.get("path", "unknown"),
                                "impact_type": "co_changed",
                                "impact_strength": 0.7,
                                "reason": "Files frequently changed together",
                                "via_commit": commit_id,
                            }
                        )

            # Remove duplicates
            seen_files = set()
            unique_impacts = []
            for impact in direct_impacts:
                if impact["file_path"] not in seen_files:
                    unique_impacts.append(impact)
                    seen_files.add(impact["file_path"])

            return unique_impacts[:8]  # Limit results

        except Exception as e:
            logger.error(f"Error finding direct impacts: {e}")
            return []

    async def _find_indirect_impacts(self, filepath: str) -> List[Dict[str, Any]]:
        """Find files that might be indirectly affected based on naming patterns and architecture"""
        indirect_impacts = []

        try:
            file_path = Path(filepath)
            file_name = file_path.stem
            file_dir = file_path.parent
            file_ext = file_path.suffix

            # Language-specific patterns
            if file_ext == ".dart":
                # Flutter patterns
                patterns_to_check = [
                    (f"{file_name}_screen.dart", "UI screen for this model", 0.6),
                    (
                        f"{file_name}_widget.dart",
                        "Widget that uses this component",
                        0.5,
                    ),
                    (f"{file_name}_service.dart", "Service layer for this model", 0.8),
                    (
                        f"{file_name}_repository.dart",
                        "Repository that manages this model",
                        0.7,
                    ),
                    (f"{file_name}_test.dart", "Test file for this component", 0.9),
                    (f"test/{file_name}_test.dart", "Test file in test directory", 0.9),
                ]

                # Check for existing files matching patterns
                for pattern, reason, strength in patterns_to_check:
                    potential_path = file_dir / pattern
                    if self._file_exists_in_graph(str(potential_path)):
                        indirect_impacts.append(
                            {
                                "file_path": str(potential_path),
                                "impact_type": "architectural_dependency",
                                "impact_strength": strength,
                                "reason": reason,
                                "pattern": pattern,
                            }
                        )

            elif file_ext == ".py":
                # Python patterns
                patterns_to_check = [
                    (f"test_{file_name}.py", "Test file for this module", 0.9),
                    (f"{file_name}_test.py", "Test file for this module", 0.9),
                    (f"{file_name}_api.py", "API layer for this service", 0.7),
                    (f"{file_name}_service.py", "Service layer implementation", 0.8),
                ]

                for pattern, reason, strength in patterns_to_check:
                    potential_path = file_dir / pattern
                    if self._file_exists_in_graph(str(potential_path)):
                        indirect_impacts.append(
                            {
                                "file_path": str(potential_path),
                                "impact_type": "architectural_dependency",
                                "impact_strength": strength,
                                "reason": reason,
                                "pattern": pattern,
                            }
                        )

            return indirect_impacts

        except Exception as e:
            logger.error(f"Error finding indirect impacts: {e}")
            return []

    async def _find_test_impacts(self, filepath: str) -> List[Dict[str, Any]]:
        """Find test files that might be affected by changes"""
        test_impacts = []

        try:
            file_path = Path(filepath)
            file_name = file_path.stem

            # Common test file patterns
            test_patterns = [
                f"test/{file_name}_test.dart",
                f"{file_name}_test.dart",
                f"test_{file_name}.py",
                f"{file_name}_test.py",
                f"tests/test_{file_name}.py",
                f"__tests__/{file_name}.test.js",
                f"spec/{file_name}_spec.rb",
            ]

            for pattern in test_patterns:
                if self._file_exists_in_graph(pattern):
                    test_impacts.append(
                        {
                            "file_path": pattern,
                            "impact_type": "test_dependency",
                            "impact_strength": 0.9,
                            "reason": "Test file that validates this component",
                            "test_type": "unit_test",
                        }
                    )

            # Look for integration tests that might import this file
            # This would require more sophisticated analysis of actual file contents

            return test_impacts

        except Exception as e:
            logger.error(f"Error finding test impacts: {e}")
            return []

    def _file_exists_in_graph(self, filepath: str) -> bool:
        """Check if file exists in knowledge graph"""
        for file_data in self.graph.nodes.get("files", {}).values():
            if file_data.get("path") == filepath:
                return True
        return False

    def _identify_critical_paths(
        self, all_impacts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify critical paths in the impact analysis"""
        critical_paths = []

        # Find high-impact files
        high_impact_files = [
            impact for impact in all_impacts if impact["impact_strength"] > 0.7
        ]

        # Group by impact type
        critical_by_type = {}
        for impact in high_impact_files:
            impact_type = impact["impact_type"]
            if impact_type not in critical_by_type:
                critical_by_type[impact_type] = []
            critical_by_type[impact_type].append(impact)

        # Create critical path summaries
        for impact_type, impacts in critical_by_type.items():
            if len(impacts) > 0:
                critical_paths.append(
                    {
                        "path_type": impact_type,
                        "affected_files": [impact["file_path"] for impact in impacts],
                        "max_impact_strength": max(
                            impact["impact_strength"] for impact in impacts
                        ),
                        "description": f"{len(impacts)} files affected via {impact_type.replace('_', ' ')}",
                    }
                )

        return critical_paths

    def _predict_from_model_change(self, filepath: str, knowledge_graph) -> list:
        """
        If the focused file is a data model, predict that related services
        and UI components will be edited next.
        """
        predictions = []
        # 1. Identify if the file is a data model (e.g., in 'models/' directory)
        if "/models/" not in filepath or not filepath.endswith(".dart"):
            return predictions

        # 2. Use the knowledge graph to find dependencies
        # Find files that have a relationship (e.g., USES) with this model file.
        for rel in self.graph.relationships:
            if rel["type"] == "USES" and rel["to"] in self.graph.nodes.get("files", {}):
                model_file = self.graph.nodes["files"][rel["to"]]
                if model_file.get("path") == filepath:
                    dependent_file = self.graph.nodes["files"][rel["from"]]
                    dep_path = dependent_file.get("path")
                    # Prioritize services and UI screens
                    if "/services/" in dep_path or "/screens/" in dep_path:
                        predictions.append(
                            {
                                "file_path": dep_path,
                                "confidence": 0.85,
                                "reason": f"Likely to edit service or UI using model {filepath}",
                                "prediction_type": "model_change_knowledge_graph",
                            }
                        )
        return predictions

    async def _predict_next_files(
        self, request: ContextRequest
    ) -> List[Dict[str, Any]]:
        """Predict which files the developer is likely to work on next"""
        try:
            next_files = []

            # New: Model change prediction using knowledge graph
            model_change_predictions = self._predict_from_model_change(
                request.filepath, self.graph
            )
            next_files.extend(model_change_predictions)

            # Based on workflow patterns
            workflow_predictions = self._predict_from_workflows(request)
            next_files.extend(workflow_predictions)

            # Based on architectural patterns
            arch_predictions = self._predict_from_architecture(request)
            next_files.extend(arch_predictions)

            # Based on recent developer patterns
            pattern_predictions = await self._predict_from_developer_patterns(request)
            next_files.extend(pattern_predictions)

            # Remove duplicates and sort by confidence
            seen_files = set()
            unique_predictions = []
            for prediction in next_files:
                if prediction["file_path"] not in seen_files:
                    unique_predictions.append(prediction)
                    seen_files.add(prediction["file_path"])

            # Sort by confidence and return top predictions
            unique_predictions.sort(key=lambda x: x["confidence"], reverse=True)
            return unique_predictions[:6]

        except Exception as e:
            logger.error(f"Error predicting next files: {e}")
            return []

    def _predict_from_workflows(self, request: ContextRequest) -> List[Dict[str, Any]]:
        """Predict next files based on common workflow patterns"""
        predictions = []

        file_path = Path(request.filepath)
        file_name = file_path.stem
        file_dir = file_path.parent

        # Check each workflow pattern
        for workflow_name, workflow_data in self.common_workflows.items():
            if file_path.suffix in workflow_data["extensions"]:
                # Determine current position in workflow
                current_step = None
                for step in workflow_data["pattern"]:
                    if step in file_name.lower():
                        current_step = step
                        break

                if current_step:
                    # Predict next steps in workflow
                    current_index = workflow_data["pattern"].index(current_step)
                    for i in range(current_index + 1, len(workflow_data["pattern"])):
                        next_step = workflow_data["pattern"][i]
                        next_file_name = file_name.replace(current_step, next_step)
                        next_file_path = (
                            file_dir / f"{next_file_name}{file_path.suffix}"
                        )

                        predictions.append(
                            {
                                "file_path": str(next_file_path),
                                "confidence": 0.7 - (i - current_index) * 0.1,
                                "reason": f"Next step in {workflow_name}",
                                "prediction_type": "workflow_pattern",
                            }
                        )

        return predictions

    def _predict_from_architecture(
        self, request: ContextRequest
    ) -> List[Dict[str, Any]]:
        """Predict next files based on architectural patterns"""
        predictions = []

        file_path = Path(request.filepath)
        file_ext = file_path.suffix
        file_name = file_path.stem.lower()

        # Select appropriate patterns based on file extension
        patterns = []
        if file_ext == ".dart":
            patterns = self.file_dependency_patterns["flutter_patterns"]
        elif file_ext == ".py":
            patterns = self.file_dependency_patterns["python_patterns"]

        # Find current file type
        current_type = None
        for pattern_type, _ in patterns:
            if pattern_type in file_name:
                current_type = pattern_type
                break

        if current_type:
            # Find likely next file types
            for pattern_type, next_types in patterns:
                if pattern_type == current_type:
                    for next_type in next_types:
                        next_file_name = file_name.replace(current_type, next_type)
                        next_file_path = (
                            file_path.parent / f"{next_file_name}{file_ext}"
                        )

                        predictions.append(
                            {
                                "file_path": str(next_file_path),
                                "confidence": 0.6,
                                "reason": f"Architectural dependency: {current_type} → {next_type}",
                                "prediction_type": "architectural_pattern",
                            }
                        )

        return predictions

    async def _predict_from_developer_patterns(
        self, request: ContextRequest
    ) -> List[Dict[str, Any]]:
        """Predict next files based on developer's historical patterns"""
        predictions = []

        dev_pattern = self.developer_workflows.get(request.developer_id, {})
        recent_files = dev_pattern.get("recent_files", [])

        if len(recent_files) >= 2:
            # Look for patterns in recent file access
            file_sequences = dev_pattern.get("file_sequences", {})
            current_file = request.filepath

            # Find sequences that start with current file
            for sequence, frequency in file_sequences.items():
                sequence_files = sequence.split(" -> ")
                if len(sequence_files) > 1 and sequence_files[0] == current_file:
                    next_file = sequence_files[1]
                    confidence = min(0.8, frequency / 10.0)  # Normalize frequency

                    predictions.append(
                        {
                            "file_path": next_file,
                            "confidence": confidence,
                            "reason": f"Developer pattern: accessed {frequency} times after {current_file}",
                            "prediction_type": "developer_history",
                        }
                    )

        return predictions

    async def _assess_change_risk(self, request: ContextRequest) -> Dict[str, Any]:
        """Assess the risk of making changes to this file"""
        try:
            risk_assessment = {
                "overall_risk": "low",
                "risk_score": 0.0,
                "risk_factors": [],
                "mitigation_suggestions": [],
            }

            risk_score = 0.0
            risk_factors = []

            # Analyze commit frequency (high frequency = higher risk)
            file_id = None
            for fid, file_data in self.graph.nodes.get("files", {}).items():
                if file_data.get("path") == request.filepath:
                    file_id = fid
                    break

            if file_id:
                commit_count = sum(
                    1
                    for rel in self.graph.relationships
                    if rel["to"] == file_id and rel["type"] == "MODIFIES"
                )

                if commit_count > 10:
                    risk_score += 0.3
                    risk_factors.append(
                        f"High change frequency ({commit_count} commits)"
                    )
                elif commit_count > 5:
                    risk_score += 0.1
                    risk_factors.append(
                        f"Moderate change frequency ({commit_count} commits)"
                    )

            # Check if multiple developers work on this file
            developers = set()
            for rel in self.graph.relationships:
                if rel["to"] == file_id and rel["type"] == "MODIFIES":
                    # Find who authored this commit
                    commit_id = rel["from"]
                    for author_rel in self.graph.relationships:
                        if (
                            author_rel["to"] == commit_id
                            and author_rel["type"] == "AUTHORED"
                        ):
                            developers.add(author_rel["from"])

            if len(developers) > 3:
                risk_score += 0.2
                risk_factors.append(
                    f"Multiple developers ({len(developers)}) work on this file"
                )

            # Check for critical file indicators
            file_path = Path(request.filepath)
            critical_indicators = ["service", "api", "auth", "payment", "security"]
            if any(
                indicator in file_path.name.lower() for indicator in critical_indicators
            ):
                risk_score += 0.2
                risk_factors.append("File appears to be critical system component")

            # Determine overall risk level
            if risk_score < 0.3:
                risk_assessment["overall_risk"] = "low"
            elif risk_score < 0.6:
                risk_assessment["overall_risk"] = "medium"
            else:
                risk_assessment["overall_risk"] = "high"

            risk_assessment["risk_score"] = min(1.0, risk_score)
            risk_assessment["risk_factors"] = risk_factors

            # Generate mitigation suggestions
            mitigation_suggestions = []
            if risk_score > 0.5:
                mitigation_suggestions.extend(
                    [
                        "Consider writing comprehensive tests before making changes",
                        "Review recent commit history to understand change patterns",
                        "Coordinate with other developers who work on this file",
                    ]
                )

            if "critical" in str(risk_factors):
                mitigation_suggestions.append(
                    "Extra caution: This appears to be a critical system file"
                )

            risk_assessment["mitigation_suggestions"] = mitigation_suggestions

            return risk_assessment

        except Exception as e:
            logger.error(f"Error assessing change risk: {e}")
            return {"error": str(e), "overall_risk": "unknown", "risk_score": 0.0}

    async def _generate_recommendations(self, request: ContextRequest) -> List[str]:
        """Generate actionable recommendations for the developer"""
        try:
            recommendations = []

            file_path = Path(request.filepath)
            file_ext = file_path.suffix

            # Language-specific recommendations
            if file_ext == ".dart":
                recommendations.extend(
                    [
                        "Consider running 'flutter analyze' to check for issues",
                        "Ensure widget tests are updated if UI changes are made",
                        "Check if this change affects the app's state management",
                    ]
                )
            elif file_ext == ".py":
                recommendations.extend(
                    [
                        "Run unit tests to ensure no regressions",
                        "Check if API documentation needs updating",
                        "Consider impact on downstream services",
                    ]
                )

            # Function-specific recommendations
            if request.function_name:
                func_name_lower = request.function_name.lower()
                if "test" in func_name_lower:
                    recommendations.append(
                        "Ensure test coverage is comprehensive and up-to-date"
                    )
                elif "api" in func_name_lower or "service" in func_name_lower:
                    recommendations.append(
                        "Check if API contracts or service interfaces need updating"
                    )
                elif "ui" in func_name_lower or "screen" in func_name_lower:
                    recommendations.append(
                        "Consider accessibility and responsive design implications"
                    )

            # General development recommendations
            recommendations.extend(
                [
                    "Review the commit history to understand recent changes",
                    "Check for related files that might need updates",
                    "Ensure proper error handling and logging",
                ]
            )

            return recommendations[:5]  # Limit to most relevant

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def _matches_workflow_pattern(
        self, file_sequence: List[str], workflow_data: Dict
    ) -> bool:
        """Check if file sequence matches a workflow pattern"""
        pattern = workflow_data["pattern"]
        if len(file_sequence) < 2:
            return False

        # Extract keywords from file names
        keywords = []
        for filepath in file_sequence:
            file_name = Path(filepath).stem.lower()
            for keyword in pattern:
                if keyword in file_name:
                    keywords.append(keyword)
                    break

        # Check if keywords follow the pattern order
        if len(keywords) >= 2:
            pattern_indices = [pattern.index(kw) for kw in keywords if kw in pattern]
            return len(pattern_indices) >= 2 and pattern_indices == sorted(
                pattern_indices
            )

        return False

    def _calculate_prediction_confidence(
        self, intent: Dict, impact: Dict, next_files: List
    ) -> float:
        """Calculate overall confidence in predictions"""
        confidence = 0.0

        # Intent confidence
        confidence += intent.get("intent_confidence", 0.0) * 0.4

        # Impact analysis confidence
        if impact.get("blast_radius_score", 0) > 0:
            confidence += 0.3

        # Next files prediction confidence
        if next_files:
            avg_file_confidence = sum(f.get("confidence", 0) for f in next_files) / len(
                next_files
            )
            confidence += avg_file_confidence * 0.3

        return min(1.0, confidence)

    async def _store_prediction(self, request: ContextRequest, result: Dict[str, Any]):
        """Store prediction for learning and analytics"""
        prediction_record = {
            "timestamp": datetime.now().isoformat(),
            "request": {
                "filepath": request.filepath,
                "developer_id": request.developer_id,
                "event_type": request.event_type,
                "function_name": request.function_name,
            },
            "prediction": {
                "intent": result.get("predicted_intent"),
                "confidence": result.get("confidence"),
                "next_files_count": len(result.get("next_likely_files", [])),
                "risk_score": result.get("risk_assessment", {}).get("risk_score", 0),
                "blast_radius": result.get("impact_analysis", {}).get(
                    "blast_radius_score", 0
                ),
            },
        }

        self.prediction_history.append(prediction_record)

        # Update developer workflow patterns
        if request.developer_id not in self.developer_workflows:
            self.developer_workflows[request.developer_id] = {
                "recent_files": [],
                "file_sequences": {},
            }

        dev_workflow = self.developer_workflows[request.developer_id]
        dev_workflow["recent_files"].append(request.filepath)

        # Keep only recent files (last 10)
        dev_workflow["recent_files"] = dev_workflow["recent_files"][-10:]

        # Update file sequences
        if len(dev_workflow["recent_files"]) >= 2:
            last_two = dev_workflow["recent_files"][-2:]
            sequence = " -> ".join(last_two)
            dev_workflow["file_sequences"][sequence] = (
                dev_workflow["file_sequences"].get(sequence, 0) + 1
            )

        # Keep only recent predictions
        if len(self.prediction_history) > 500:
            self.prediction_history = self.prediction_history[-250:]

    async def get_prediction_accuracy(self) -> Dict[str, Any]:
        """Get prediction accuracy statistics"""
        if not self.prediction_history:
            return {"status": "no_data", "total_predictions": 0}

        total_predictions = len(self.prediction_history)
        recent_predictions = [
            p
            for p in self.prediction_history
            if datetime.fromisoformat(p["timestamp"])
            > datetime.now() - timedelta(hours=24)
        ]

        avg_confidence = (
            sum(p["prediction"]["confidence"] for p in recent_predictions)
            / len(recent_predictions)
            if recent_predictions
            else 0
        )
        avg_risk_score = (
            sum(p["prediction"]["risk_score"] for p in recent_predictions)
            / len(recent_predictions)
            if recent_predictions
            else 0
        )

        return {
            "total_predictions": total_predictions,
            "predictions_last_24h": len(recent_predictions),
            "average_confidence": avg_confidence,
            "average_risk_score": avg_risk_score,
            "unique_developers_tracked": len(self.developer_workflows),
            "workflow_patterns_learned": sum(
                len(wf.get("file_sequences", {}))
                for wf in self.developer_workflows.values()
            ),
            "accuracy_status": "operational",
        }
