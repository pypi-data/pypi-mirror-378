#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QQaS CLI reporter"""

# pylint: disable=C0301,C0302,R0911,R0912

import json
import os
import typing as t

from . import __version__
from ._colours import COLOURS_AVAILABLE, Fore, Style
from .constructs.complexity import ComplexityHotspot
from .constructs.duplication import DuplicationResult
from .constructs.full import FileAnalysisResult, ProjectAnalysisResult
from .constructs.security import SecurityIssue

__all__: t.Tuple[str, ...] = ("CQaSReporter",)


class CQaSReporter:
    """Professional reporter with comprehensive output formatting"""

    def __init__(self, colour: bool = True, feedback: bool = True, top_n: int = 10):
        self.colour = colour and COLOURS_AVAILABLE
        self.top_n: int = top_n
        self.feedback: bool = feedback

    def _colourise(self, text: str, colour: str) -> str:
        """Apply colour if available"""
        if not self.colour:
            return text
        colour_map: t.Dict[str, str] = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
            "bright": Style.BRIGHT,
            "dim": Style.DIM,
        }
        return f"{colour_map.get(colour, '')}{text}{Style.RESET_ALL}"

    def _get_severity_colour(self, severity: str) -> str:
        """Get colour for security severity"""
        severity_colours: t.Dict[str, str] = {
            "CRITICAL": "red",
            "HIGH": "yellow",
            "MEDIUM": "blue",
            "LOW": "cyan",
        }
        return severity_colours.get(severity, "cyan")

    def _get_number_colour(self, value: float, value_type: str = "general") -> str:
        """Get appropriate colour for numeric values based on type and range"""

        if value_type == "percentage":
            if value >= 90:
                return "green"
            if value >= 75:
                return "cyan"
            if value >= 50:
                return "yellow"
            return "red"
        if value_type == "ipercentage":
            if value <= 10:
                return "green"
            if value <= 25:
                return "cyan"
            if value <= 50:
                return "yellow"
            return "red"
        if value_type == "quality_score":
            if value >= 90:
                return "green"
            if value >= 80:
                return "cyan"
            if value >= 60:
                return "yellow"
            return "red"
        if value_type == "security_score":
            if value >= 95:
                return "green"
            if value >= 85:
                return "cyan"
            if value >= 75:
                return "yellow"
            return "red"
        if value_type == "complexity":
            if value <= 10:
                return "green"
            if value <= 20:
                return "cyan"
            if value <= 50:
                return "yellow"
            return "red"
        if value_type == "debt_hours":
            if value <= 1:
                return "green"
            if value <= 5:
                return "cyan"
            if value <= 15:
                return "yellow"
            return "red"
        if value_type == "cvss":
            if value <= 3.9:
                return "cyan"
            if value <= 6.9:
                return "yellow"
            if value <= 8.9:
                return "yellow"
            return "red"
        if value_type == "count":
            if value == 0:
                return "green"
            if value <= 5:
                return "cyan"
            if value <= 15:
                return "yellow"
            return "red"
        return "cyan"

    def generate_comprehensive_report(
        self, project_result: ProjectAnalysisResult
    ) -> str:
        """Generate comprehensive textual report with reversed layout"""
        lines: t.List[str] = []

        # Detailed Analysis Section (Top Priority)
        lines.extend(self._generate_security_analysis_section(project_result))
        lines.extend(self._generate_complexity_hotspots_section(project_result))
        lines.extend(self._generate_problematic_files_section(project_result))
        lines.extend(self._generate_technical_debt_section(project_result))
        lines.extend(self._generate_detailed_statistics_section(project_result))
        lines.extend(self._generate_quality_distribution_section(project_result))
        lines.extend(self._generate_recommendations_section(project_result))

        # Summary Sections (Bottom)
        lines.extend(self._generate_average_metrics_section(project_result))
        lines.extend(self._generate_verdicts_section(project_result))
        lines.extend(self._generate_executive_summary_section(project_result))

        # Header and Footer
        header_lines: t.List[str] = [
            self._colourise("=" * 80, "bright"),
            self._colourise("PYTHON CODE QUALITY & SECURITY ANALYSIS REPORT", "bright"),
            self._colourise("=" * 80, "bright"),
            "",
            "",
        ]

        footer_lines: t.List[str] = [
            "",
            self._colourise("=" * 80, "bright"),
            f"Analysis completed in {self._colourise(f'{project_result.analysis_duration:.2f}s', 'bright')}. "
            f"Report generated by the CQaS analyser {self._colourise(f'v{__version__}', 'bright')}",
            self._colourise("=" * 80, "bright"),
        ]

        return "\n".join(header_lines + lines + footer_lines)

    def _generate_security_analysis_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate detailed security analysis section"""

        lines: t.List[str] = []

        # Collect all security issues
        all_security_issues: t.List[t.Tuple[str, SecurityIssue]] = []
        for result in project_result.file_results:
            for issue in result.security_issues:
                all_security_issues.append((result.file_path, issue))

        if not all_security_issues:
            return lines

        # Sort by severity and CVSS score
        severity_order: t.Dict[str, int] = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }
        all_security_issues.sort(
            key=lambda x: (
                severity_order.get(x[1].severity.severity_name, 0),
                x[1].cvss_score,
            ),
            reverse=True,
        )

        lines.extend(
            [
                self._colourise("DETAILED SECURITY ANALYSIS", "bright"),
                self._colourise("-" * 60, "dim"),
                "",
            ]
        )

        # Security summary by severity
        severity_counts: t.Dict[str, int] = project_result.security_issues_by_severity
        lines.extend(
            [
                "Security Issues by Severity:",
                f"  {self._colourise('CRITICAL', 'red')}: {severity_counts.get('CRITICAL', 0)} issues",
                f"  {self._colourise('HIGH', 'yellow')}: {severity_counts.get('HIGH', 0)} issues",
                f"  {self._colourise('MEDIUM', 'blue')}: {severity_counts.get('MEDIUM', 0)} issues",
                f"  {self._colourise('LOW', 'cyan')}: {severity_counts.get('LOW', 0)} issues",
                "",
            ]
        )

        # Top security issues with details
        lines.extend(
            [
                f"Top {min(15, len(all_security_issues))} Security Issues (by severity & CVSS score):",
                self._colourise("-" * 50, "dim"),
            ]
        )

        for file_path, issue in all_security_issues[: self.top_n + 10]:
            file_name: str = os.path.basename(file_path)
            severity_colour: str = self._get_severity_colour(
                issue.severity.severity_name
            )

            lines.extend(
                [
                    f"[{self._colourise(issue.severity.severity_name, severity_colour)}] "
                    f"{file_name}:{self._colourise(str(issue.line_number), 'cyan')} - {issue.description}",
                    f"  CVSS Score: {issue.cvss_score} | "
                    f"Confidence: {issue.confidence.name if hasattr(issue.confidence, 'name') else issue.confidence}",
                    f"  Remediation: {issue.remediation or 'No specific remediation provided'}",
                ]
            )

            if issue.code_snippet:
                lines.append(f"  Code: {issue.code_snippet[:100]}")

            lines.append("")

        if len(all_security_issues) > 15:
            remaining: int = len(all_security_issues) - 15
            lines.append(
                f"... and {self._colourise(str(remaining), 'cyan')} more security issues"
            )

        lines.append("")
        return lines

    def _generate_complexity_hotspots_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate complexity hotspots section"""

        lines: t.List[str] = []

        # Collect all complexity hotspots
        all_hotspots: t.List[t.Tuple[str, ComplexityHotspot]] = []
        for result in project_result.file_results:
            for hotspot in result.quality_metrics.complexity_hotspots:
                all_hotspots.append((result.file_path, hotspot))

        if not all_hotspots:
            return lines

        # Sort by complexity
        all_hotspots.sort(key=lambda x: x[1].complexity or 0, reverse=True)

        lines.extend(
            [
                self._colourise("COMPLEXITY HOTSPOTS ANALYSIS", "bright"),
                self._colourise("-" * 60, "dim"),
                "",
            ]
        )

        # Show top complexity hotspots
        lines.extend(
            [
                f"Top {min(self.top_n, len(all_hotspots))} Complexity Hotspots:",
                self._colourise("-" * 40, "dim"),
            ]
        )

        for file_path, hotspot in all_hotspots[: self.top_n]:
            file_name: str = os.path.basename(file_path)

            if hotspot.complexity:
                complexity_colour: str = (
                    "red"
                    if hotspot.complexity > 20
                    else "yellow" if hotspot.complexity > 10 else "cyan"
                )
                lines.append(
                    f"{hotspot.type.name if hasattr(hotspot.type, 'name') else hotspot.type} "
                    f"'{hotspot.name}' in {self._colourise(f'{file_name}:{hotspot.line}', 'bright')}  - "
                    f"Complexity: {self._colourise(str(hotspot.complexity), complexity_colour)}"
                )
            elif hotspot.method_count:
                lines.append(
                    f"CLASS '{hotspot.name}' in {self._colourise(f'{file_name}:{hotspot.line}', 'bright')} - "
                    f"{self._colourise(str(hotspot.method_count), self._get_number_colour(hotspot.method_count, 'count'))} methods"
                )

        lines.extend(["", ""])
        return lines

    def _generate_problematic_files_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate problematic files section"""

        lines: t.List[str] = []

        # Calculate issue scores for files
        files_with_scores: t.List[t.Tuple[FileAnalysisResult, float]] = []
        for result in project_result.file_results:
            issue_score: float = (
                len(result.security_issues) * 3  # Security issues weighted higher
                + len(result.dead_code_info) * 2
                + len(result.pep8_result.issues)
                + (result.quality_metrics.cyclomatic_complexity // 10)
                + (result.duplication_percentage // 5)
            )

            if issue_score > 0:
                files_with_scores.append((result, issue_score))

        if not files_with_scores:
            return lines

        files_with_scores.sort(key=lambda x: x[1], reverse=True)

        lines.extend(
            [
                self._colourise("FILES REQUIRING IMMEDIATE ATTENTION", "bright"),
                self._colourise("-" * 60, "dim"),
                "",
            ]
        )

        # Show top problematic files with detailed breakdown
        for result, issue_score in files_with_scores[: self.top_n]:
            file_name: str = os.path.basename(result.file_path)
            quality_score: float = result.get_overall_quality_score()
            security_score: float = result.get_security_score()

            # Determine quality colour
            quality_colour: str = (
                "green"
                if quality_score >= 80
                else "yellow" if quality_score >= 60 else "red"
            )

            lines.extend(
                [
                    f"File: {self._colourise(file_name, 'bright')} (Issue Score: {issue_score})",
                    f"  Quality: {self._colourise(f'{quality_score:.1f}/100', quality_colour)} | "
                    f"Security: {self._colourise(f'{security_score:.1f}/100', self._get_number_colour(security_score, 'security_score'))} | "
                    f"Maintainability: {self._colourise(result.get_maintainability_category(), 'bright')}",
                    f"  Complexity: {self._colourise(str(result.quality_metrics.cyclomatic_complexity), self._get_number_colour(result.quality_metrics.cyclomatic_complexity, 'complexity'))} | "
                    f"Lines: {self._colourise(str(result.quality_metrics.lines_of_code), 'cyan')} | "
                    f"Tech Debt: {self._colourise(f'{result.quality_metrics.technical_debt_ratio:.1f}%', self._get_number_colour(result.quality_metrics.technical_debt_ratio, 'ipercentage'))}",
                ]
            )

            # Issue breakdown
            issue_details: t.List[str] = []
            if result.security_issues:
                issue_details.append(
                    f"Security: {self._colourise(str(len(result.security_issues)), self._get_number_colour(len(result.security_issues), 'count'))}"
                )
            if result.dead_code_info:
                issue_details.append(
                    f"Dead Code: {self._colourise(str(len(result.dead_code_info)), self._get_number_colour(len(result.dead_code_info), 'count'))}"
                )
            if result.pep8_result.issues:
                issue_details.append(
                    f"Style: {self._colourise(str(len(result.pep8_result.issues)), self._get_number_colour(len(result.pep8_result.issues), 'count'))}"
                )
            if result.duplication_percentage > 3:
                issue_details.append(
                    f"Duplication: {self._colourise(f'{result.duplication_percentage:.1f}%', self._get_number_colour(result.duplication_percentage, 'percentage'))}"
                )

            if issue_details:
                lines.append(f"  Issues: {' | '.join(issue_details)}")

            lines.append("")

        return lines + [""]

    def _generate_technical_debt_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate technical debt analysis section"""

        lines: t.List[str] = []

        lines.extend(
            [
                self._colourise("TECHNICAL DEBT ANALYSIS", "bright"),
                self._colourise("-" * 60, "dim"),
                f"Total Estimated Debt: {self._colourise(f'{project_result.total_technical_debt_hours:.1f} hours', self._get_number_colour(project_result.total_technical_debt_hours, 'debt_hours'))}",
                f"Average Debt Ratio: {self._colourise(f'{project_result.avg_technical_debt_ratio:.1f}%', self._get_number_colour(project_result.avg_technical_debt_ratio, 'ipercentage'))}",
                "",
            ]
        )

        # Debt breakdown by file
        debt_files: t.List[t.Tuple[FileAnalysisResult, float]] = [
            (r, r.quality_metrics.technical_debt_minutes)
            for r in project_result.file_results
        ]
        debt_files.sort(key=lambda x: x[1], reverse=True)

        if debt_files:
            lines.extend(
                ["Files with Highest Technical Debt:", self._colourise("-" * 40, "dim")]
            )

            for result, debt_minutes in debt_files[: self.top_n]:
                file_name: str = os.path.basename(result.file_path)
                debt_hours: float = debt_minutes / 60.0
                debt_colour: str = (
                    "red" if debt_hours > 2 else "yellow" if debt_hours > 1 else "cyan"
                )

                lines.append(
                    f"{file_name}: {self._colourise(f'{debt_hours:.1f}h', debt_colour)} "
                    f"(Ratio: {self._colourise(f'{result.quality_metrics.technical_debt_ratio:.1f}%', self._get_number_colour(result.quality_metrics.technical_debt_ratio, 'ipercentage'))})"
                )

        lines.extend(["", ""])
        return lines

    def _generate_detailed_statistics_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate comprehensive statistics section"""
        lines: t.List[str] = []
        lines.extend(
            [
                self._colourise("COMPREHENSIVE PROJECT STATISTICS", "bright"),
                self._colourise("-" * 60, "dim"),
                "",
            ]
        )
        # File statistics
        lines.extend(
            [
                "File Analysis:",
                f"  Files Found: {self._colourise(f'{project_result.total_files_found:,}', 'cyan')}",
                f"  Files Analysed: {self._colourise(f'{project_result.files_analysed:,}', 'cyan')}",
                f"  Files with Errors: {self._colourise(str(project_result.files_with_errors), self._get_number_colour(project_result.files_with_errors, 'count'))}",
                f"  Analysis Duration: {self._colourise(f'{project_result.analysis_duration:.2f} seconds', 'bright')}",
                "",
            ]
        )
        # Code statistics
        lines.extend(
            [
                "Code Structure:",
                f"  Total Lines: {self._colourise(f'{project_result.total_lines:,}', 'cyan')}",
                f"  Logical Lines: {self._colourise(f'{project_result.total_logical_lines:,}', 'cyan')}",
                f"  Functions: {self._colourise(f'{project_result.total_functions:,}', 'cyan')}",
                f"  Classes: {self._colourise(f'{project_result.total_classes:,}', 'cyan')}",
                "",
            ]
        )
        # Quality metrics
        if project_result.file_results:
            avg_complexity: float = sum(
                r.quality_metrics.cyclomatic_complexity
                for r in project_result.file_results
            ) / len(project_result.file_results)
            avg_maintainability: float = sum(
                r.quality_metrics.maintainability_index
                for r in project_result.file_results
            ) / len(project_result.file_results)
            avg_readability: float = sum(
                r.readability_metrics.score for r in project_result.file_results
            ) / len(project_result.file_results)
            avg_duplication: float = sum(
                r.duplication_percentage for r in project_result.file_results
            ) / len(project_result.file_results)
            lines.extend(
                [
                    "Average Quality Metrics:",
                    f"  Cyclomatic Complexity: {self._colourise(f'{avg_complexity:.1f}', self._get_number_colour(avg_complexity, 'complexity'))}",
                    f"  Maintainability Index: {self._colourise(f'{avg_maintainability:.1f}/100', self._get_number_colour(avg_maintainability, 'quality_score'))}",
                    f"  Readability Score: {self._colourise(f'{avg_readability:.1f}/100', self._get_number_colour(avg_readability, 'quality_score'))}",
                    f"  Code Duplication: {self._colourise(f'{avg_duplication:.1f}%', self._get_number_colour(avg_duplication, 'percentage'))}",
                    "",
                ]
            )
        # Issue statistics
        lines.extend(
            [
                "Issue Summary:",
                f"  Security Issues: {self._colourise(str(project_result.total_security_issues), self._get_number_colour(project_result.total_security_issues, 'count'))}",
                f"  Style Issues: {self._colourise(str(project_result.total_style_issues), self._get_number_colour(project_result.total_style_issues, 'count'))}",
                f"  Dead Code Items: {self._colourise(str(project_result.total_dead_code_items), self._get_number_colour(project_result.total_dead_code_items, 'count'))}",
                "",
            ]
        )
        # Duplication analysis
        dup: DuplicationResult = project_result.duplication_result
        lines.extend(
            [
                "Project Duplication Analysis:",
                f"  Duplicate Blocks: {self._colourise(str(dup.duplicate_blocks_count), self._get_number_colour(dup.duplicate_blocks_count, 'count'))}",
                f"  Duplicated Lines (est.): {self._colourise(f'{dup.duplicated_lines_estimate:,}', 'cyan')}",
                f"  Total Code Lines: {self._colourise(f'{dup.total_code_lines:,}', 'cyan')}",
                f"  Duplication Percentage: {self._colourise(f'{dup.duplication_percentage:.1f}%', self._get_number_colour(dup.duplication_percentage, 'percentage'))}",
                "",
            ]
        )
        return lines + [""]

    def _generate_quality_distribution_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate quality distribution section"""

        lines: t.List[str] = []

        lines.extend(
            [
                self._colourise("QUALITY DISTRIBUTION ANALYSIS", "bright"),
                self._colourise("-" * 60, "dim"),
                "",
            ]
        )

        # Quality score distribution
        quality_dist: t.Dict[str, int] = project_result.quality_distribution
        lines.extend(
            [
                "Quality Score Distribution:",
                f"  {self._colourise('Excellent', 'green')} (90-100): {self._colourise(str(quality_dist.get('Excellent', 0)), 'green')} files",
                f"  {self._colourise('Good', 'cyan')} (75-89): {self._colourise(str(quality_dist.get('Good', 0)), 'cyan')} files",
                f"  {self._colourise('Fair', 'yellow')} (60-74): {self._colourise(str(quality_dist.get('Fair', 0)), 'yellow')} files",
                f"  {self._colourise('Poor', 'yellow')} (40-59): {self._colourise(str(quality_dist.get('Poor', 0)), 'yellow')} files",
                f"  {self._colourise('Critical', 'red')} (0-39): {self._colourise(str(quality_dist.get('Critical', 0)), 'red')} files",
                "",
            ]
        )

        # Complexity distribution
        complexity_dist: t.Dict[str, int] = project_result.complexity_distribution
        lines.extend(
            [
                "Complexity Distribution:",
                f"  {self._colourise('Simple', 'green')} (≤10): {self._colourise(str(complexity_dist.get('Simple', 0)), 'green')} files",
                f"  {self._colourise('Moderate', 'cyan')} (11-20): {self._colourise(str(complexity_dist.get('Moderate', 0)), 'cyan')} files",
                f"  {self._colourise('Complex', 'yellow')} (21-50): {self._colourise(str(complexity_dist.get('Complex', 0)), 'yellow')} files",
                f"  {self._colourise('Very Complex', 'red')} (>50): {self._colourise(str(complexity_dist.get('Very Complex', 0)), 'red')} files",
                "",
            ]
        )

        # Maintainability distribution
        maint_dist: t.Dict[str, int] = project_result.maintainability_distribution
        lines.extend(
            [
                "Maintainability Distribution:",
                f"  {self._colourise('Excellent', 'green')} (≥85): {self._colourise(str(maint_dist.get('Excellent', 0)), 'green')} files",
                f"  {self._colourise('Good', 'cyan')} (70-84): {self._colourise(str(maint_dist.get('Good', 0)), 'cyan')} files",
                f"  {self._colourise('Fair', 'yellow')} (55-69): {self._colourise(str(maint_dist.get('Fair', 0)), 'yellow')} files",
                f"  {self._colourise('Poor', 'yellow')} (25-54): {self._colourise(str(maint_dist.get('Poor', 0)), 'yellow')} files",
                f"  {self._colourise('Legacy', 'red')} (<25): {self._colourise(str(maint_dist.get('Legacy', 0)), 'red')} files",
                "",
            ]
        )

        return lines + [""]

    def _generate_recommendations_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate actionable recommendations"""

        if not self.feedback:
            return []

        lines: t.List[str] = []

        recommendations = self._calculate_recommendations(project_result)

        if not recommendations:
            return lines

        lines.extend(
            [
                self._colourise("ACTIONABLE RECOMMENDATIONS", "bright"),
                self._colourise("-" * 60, "dim"),
                "",
            ]
        )

        for idx, recommendation in enumerate(recommendations, 1):
            priority_colour: str = (
                "red"
                if recommendation["priority"] == "HIGH"
                else "yellow" if recommendation["priority"] == "MEDIUM" else "cyan"
            )

            lines.extend(
                [
                    f"{idx}. [{self._colourise(recommendation['priority'], priority_colour)}] {recommendation['title']}",
                    f"   {recommendation['description']}",
                    f"   Action: {recommendation['action']}",
                    "",
                ]
            )

        return lines

    def _calculate_recommendations(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[t.Dict[str, str]]:
        """Calculate actionable recommendations based on analysis"""

        recommendations: t.List[t.Dict[str, str]] = []

        # Critical security issues
        critical_security: int = project_result.security_issues_by_severity.get(
            "CRITICAL", 0
        )
        high_security: int = project_result.security_issues_by_severity.get("HIGH", 0)

        if critical_security > 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "title": "Critical Security Vulnerabilities",
                    "description": f"{self._colourise(str(critical_security), 'red')} critical security issues require immediate attention.",
                    "action": "Review and fix all critical security issues before deployment. Consider security audit.",
                }
            )

        if high_security > 5:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "title": "High Severity Security Issues",
                    "description": f"{self._colourise(str(high_security), 'yellow')} high-severity security vulnerabilities detected.",
                    "action": "Implement security code review process and address high-severity issues systematically.",
                }
            )

        # Complexity issues
        complex_files: int = project_result.complexity_distribution.get(
            "Very Complex", 0
        )
        if complex_files > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "title": "High Complexity Code",
                    "description": f"{self._colourise(str(complex_files), 'red')} files have very high complexity (>50).",
                    "action": "Refactor complex functions into smaller, focused methods. Consider applying SOLID principles.",
                }
            )

        # Technical debt
        if project_result.total_technical_debt_hours > 40:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "title": "Significant Technical Debt",
                    "description": f"Estimated {self._colourise(f'{project_result.total_technical_debt_hours:.1f} hours', self._get_number_colour(project_result.total_technical_debt_hours, 'debt_hours'))} of technical debt.",
                    "action": "Allocate dedicated sprint time for technical debt reduction. Prioritise by impact and effort.",
                }
            )

        # Code duplication
        if project_result.duplication_result.duplication_percentage > 10:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "title": "Code Duplication",
                    "description": f"{self._colourise(f'{project_result.duplication_result.duplication_percentage:.1f}%', self._get_number_colour(project_result.duplication_result.duplication_percentage, 'percentage'))} code duplication detected.",
                    "action": "Extract common functionality into reusable functions or classes. Consider design patterns.",
                }
            )

        # Documentation
        if project_result.file_results:
            avg_docstring: float = sum(
                r.readability_metrics.docstring_coverage
                for r in project_result.file_results
            ) / len(project_result.file_results)
            if avg_docstring < 50:
                recommendations.append(
                    {
                        "priority": "LOW",
                        "title": "Documentation Coverage",
                        "description": f"Low docstring coverage ({self._colourise(f'{avg_docstring:.1f}%', 'red')}) detected.",
                        "action": "Add comprehensive docstrings to public functions and classes. Consider documentation standards.",
                    }
                )

        return recommendations[: self.top_n]  # Limit to top recommendations

    def _generate_average_metrics_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate average metrics section"""
        lines: t.List[str] = []
        if not project_result.file_results:
            return lines
        results: t.List[FileAnalysisResult] = project_result.file_results
        # Calculate averages
        avg_complexity: float = sum(
            r.quality_metrics.cyclomatic_complexity for r in results
        ) / len(results)
        avg_maintainability: float = sum(
            r.quality_metrics.maintainability_index for r in results
        ) / len(results)
        avg_tech_debt: float = sum(
            r.quality_metrics.technical_debt_ratio for r in results
        ) / len(results)
        avg_duplication: float = sum(r.duplication_percentage for r in results) / len(
            results
        )
        avg_readability: float = sum(
            r.readability_metrics.score for r in results
        ) / len(results)
        avg_quality: float = sum(r.get_overall_quality_score() for r in results) / len(
            results
        )
        lines.extend(
            [
                self._colourise("AVERAGE METRICS", "bright"),
                self._colourise("-" * 40, "dim"),
                f"Cyclomatic Complexity: {self._colourise(f'{avg_complexity:.1f}', self._get_number_colour(avg_complexity, 'complexity'))}",
                f"Maintainability Index: {self._colourise(f'{avg_maintainability:.1f}/100', self._get_number_colour(avg_maintainability, 'quality_score'))}",
                f"Technical Debt Ratio: {self._colourise(f'{avg_tech_debt:.1f}%', self._get_number_colour(avg_tech_debt, 'debt_percentage'))}",
                f"Code Duplication: {self._colourise(f'{avg_duplication:.1f}%', self._get_number_colour(avg_duplication, 'percentage'))}",
                f"Readability Score: {self._colourise(f'{avg_readability:.1f}/100', self._get_number_colour(avg_readability, 'quality_score'))}",
                f"Code Quality Index: {self._colourise(f'{avg_quality:.1f}/100', self._get_number_colour(avg_quality, 'quality_score'))}",
                "",
            ]
        )
        return lines

    def _generate_verdicts_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate verdicts section"""

        if not self.feedback:
            return []

        lines: t.List[str] = []

        overall_quality = project_result.get_overall_project_quality()
        overall_security = project_result.get_overall_project_security()

        # Generate verdicts
        verdicts: t.Dict[str, str] = {
            "overall": self._generate_overall_verdict(
                overall_quality, overall_security, project_result
            ),
            "quality": self._generate_quality_verdict(overall_quality),
            "security": self._generate_security_verdict(
                overall_security, project_result
            ),
            "maintainability": self._generate_maintainability_verdict(project_result),
            "complexity": self._generate_complexity_verdict(project_result),
        }

        lines.extend(
            [
                self._colourise("VERDICTS", "bright"),
                self._colourise("-" * 40, "dim"),
                f"Overall: {self._colourise(verdicts['overall'], 'bright')}",
                f"Quality: {self._colourise(verdicts['quality'], 'bright')}",
                f"Security: {self._colourise(verdicts['security'], 'bright')}",
                f"Maintainability: {self._colourise(verdicts['maintainability'], 'bright')}",
                f"Complexity: {self._colourise(verdicts['complexity'], 'bright')}",
                "",
            ]
        )

        return lines

    def _generate_executive_summary_section(
        self, project_result: ProjectAnalysisResult
    ) -> t.List[str]:
        """Generate executive summary section"""
        lines: t.List[str] = []
        overall_quality: float = project_result.get_overall_project_quality()
        overall_security: float = project_result.get_overall_project_security()
        critical_issues: int = project_result.security_issues_by_severity.get(
            "CRITICAL", 0
        )
        high_issues: int = project_result.security_issues_by_severity.get("HIGH", 0)
        bad_issues: int = critical_issues + high_issues
        lines.extend(
            [
                self._colourise("EXECUTIVE SUMMARY", "bright"),
                self._colourise("-" * 40, "dim"),
                f"Files Analysed: {self._colourise(str(project_result.files_analysed), 'cyan')}",
                f"Total Lines of Code: {self._colourise(f'{project_result.total_lines:,}', 'cyan')}",
                f"Overall Quality Index: {self._colourise(f'{overall_quality:.2f}/100', self._get_number_colour(overall_quality, 'quality_score'))}",
                f"Overall Security Score: {self._colourise(f'{overall_security:.1f}/100', self._get_number_colour(overall_security, 'security_score'))}",
                f"Security Issues Found: {self._colourise(str(project_result.total_security_issues), self._get_number_colour(project_result.total_security_issues, 'count'))} "
                f"({self._colourise(str(bad_issues), 'green' if bad_issues == 0 else 'red')} high/critical)",
                "",
            ]
        )
        return lines

    def _generate_overall_verdict(
        self,
        quality_score: float,
        security_score: float,
        project_result: ProjectAnalysisResult,
    ) -> str:
        """Generate overall project verdict"""

        combined_score: float = (quality_score * 0.6) + (security_score * 0.4)
        critical_issues: int = project_result.security_issues_by_severity.get(
            "CRITICAL", 0
        )

        if critical_issues > 0:
            return "Critical: Security vulnerabilities require immediate attention"
        if combined_score >= 90:
            return "Excellent: Outstanding codebase ready for production"
        if combined_score >= 80:
            return "Very Good: High-quality, secure codebase ready for production"
        if combined_score >= 70:
            return "Good: Solid codebase with minor improvements needed"
        if combined_score >= 60:
            return "Acceptable: Moderate quality, requires attention before production"
        if combined_score >= 40:
            return "Poor: Significant issues present, major improvements needed"
        return "Critical: Severe quality and security issues, immediate action required"

    def _generate_quality_verdict(self, quality_score: float) -> str:
        """Generate quality verdict"""

        if quality_score >= 90:
            return "Exceptional: Exemplary code structure and maintainability"
        if quality_score >= 80:
            return "Excellent: Well-structured, highly maintainable code"
        if quality_score >= 70:
            return "Good: Generally well-written with room for improvement"
        if quality_score >= 60:
            return "Acceptable: Adequate quality, some refactoring recommended"
        if quality_score >= 40:
            return "Poor: Quality issues present, refactoring needed"
        return "Critical: Severe quality issues, major refactoring required"

    def _generate_security_verdict(
        self, security_score: float, project_result: ProjectAnalysisResult
    ) -> str:
        """Generate security verdict"""

        critical_count: int = project_result.security_issues_by_severity.get(
            "CRITICAL", 0
        )
        high_count: int = project_result.security_issues_by_severity.get("HIGH", 0)

        if critical_count > 0:
            return f"Critical: {self._colourise(str(critical_count), 'red')} critical vulnerabilities require immediate attention"
        if high_count > 10:
            return f"Poor: {self._colourise(str(high_count), 'yellow')} high-severity vulnerabilities found"
        if high_count > 5:
            return f"Concerning: {self._colourise(str(high_count), 'yellow')} high-severity security issues present"
        if high_count > 0:
            return f"Attention Needed: {self._colourise(str(high_count), 'yellow')} high-severity issues require review"
        if security_score >= 95:
            return "Excellent: Outstanding security posture"
        if security_score >= 85:
            return "Very Good: Strong security practices implemented"
        if security_score >= 75:
            return "Good: Generally secure with minor issues to address"
        if security_score >= 60:
            return "Acceptable: Some security concerns to address"
        return "Poor: Multiple security vulnerabilities present"

    def _generate_maintainability_verdict(
        self, project_result: ProjectAnalysisResult
    ) -> str:
        """Generate maintainability verdict"""

        if not project_result.file_results:
            return "Unknown: No files analysed"

        avg_maintainability: float = sum(
            r.quality_metrics.maintainability_index for r in project_result.file_results
        ) / len(project_result.file_results)

        if avg_maintainability >= 85:
            return "Excellent: Highly maintainable codebase"
        if avg_maintainability >= 70:
            return "Good: Well-maintainable with minor improvements possible"
        if avg_maintainability >= 55:
            return "Acceptable: Moderately maintainable"
        if avg_maintainability >= 25:
            return "Poor: Maintenance challenges present"
        return "Critical: Severely difficult to maintain"

    def _generate_complexity_verdict(
        self, project_result: ProjectAnalysisResult
    ) -> str:
        """Generate complexity verdict"""

        if not project_result.file_results:
            return "Unknown: No files analysed"

        avg_complexity: float = sum(
            r.quality_metrics.cyclomatic_complexity for r in project_result.file_results
        ) / len(project_result.file_results)

        if avg_complexity <= 10:
            return "Excellent: Low complexity, easy to understand"
        if avg_complexity <= 15:
            return "Good: Moderate complexity, generally manageable"
        if avg_complexity <= 25:
            return "Acceptable: Higher complexity, consider refactoring"
        if avg_complexity <= 40:
            return "Poor: High complexity, refactoring recommended"
        return "Critical: Excessive complexity, immediate refactoring needed"

    def generate_json_report(self, project_result: ProjectAnalysisResult) -> str:
        """Generate comprehensive JSON report"""

        data: t.Dict[str, t.Any] = {
            "project_info": {
                "path": project_result.project_path,
                "analysis_duration": project_result.analysis_duration,
                "files_found": project_result.total_files_found,
                "files_analysed": project_result.files_analysed,
                "files_with_errors": project_result.files_with_errors,
            },
            "summary": {
                "overall_quality_score": project_result.get_overall_project_quality(),
                "overall_security_score": project_result.get_overall_project_security(),
                "total_lines": project_result.total_lines,
                "total_security_issues": project_result.total_security_issues,
                "total_technical_debt_hours": project_result.total_technical_debt_hours,
            },
            "distributions": {
                "quality": project_result.quality_distribution,
                "complexity": project_result.complexity_distribution,
                "maintainability": project_result.maintainability_distribution,
                "security_by_severity": project_result.security_issues_by_severity,
            },
            "duplication_analysis": {
                "duplicate_blocks": project_result.duplication_result.duplicate_blocks_count,
                "duplicated_lines": project_result.duplication_result.duplicated_lines_estimate,
                "duplication_percentage": project_result.duplication_result.duplication_percentage,
            },
            "files": [],
        }

        # Add file-level data
        for result in project_result.file_results:
            file_data: t.Dict[str, t.Any] = {
                "path": result.file_path,
                "analysis_time": result.analysis_time,
                "syntax_errors": result.syntax_errors,
                "quality_score": result.get_overall_quality_score(),
                "security_score": result.get_security_score(),
                "metrics": result.quality_metrics.__dict__,
                "security_issues": [
                    {
                        "line": issue.line_number,
                        "type": issue.vulnerability_type.vuln_type,
                        "description": issue.description,
                        "cvss_score": issue.cvss_score,
                        "severity": issue.severity.severity_name,
                        "confidence": (
                            issue.confidence.name
                            if hasattr(issue.confidence, "name")
                            else str(issue.confidence)
                        ),
                        "remediation": issue.remediation,
                        "code_snippet": issue.code_snippet,
                    }
                    for issue in result.security_issues
                ],
                "dead_code": [
                    {
                        "line": item.line_number,
                        "type": (
                            item.element_type.name
                            if hasattr(item.element_type, "name")
                            else str(item.element_type)
                        ),
                        "name": item.element_name,
                        "reason": item.reason,
                        "confidence": (
                            item.confidence.name
                            if hasattr(item.confidence, "name")
                            else str(item.confidence)
                        ),
                    }
                    for item in result.dead_code_info
                ],
                "style_issues": [
                    {
                        "line": issue.line,
                        "column": issue.column,
                        "message": issue.message,
                    }
                    for issue in result.pep8_result.issues
                ],
            }
            data["files"].append(file_data)

        return json.dumps(data, indent=4, default=str)
