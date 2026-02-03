"""Formatters for converting findings to human-readable output."""
from typing import Dict, Any, List, Optional
from datetime import datetime


class FindingFormatter:
    """Formats findings for display and reporting."""
    
    @staticmethod
    def format_finding(finding: Dict[str, Any], citation: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a single finding as human-readable text.
        
        Args:
            finding: Finding dictionary from database
            citation: Optional citation dictionary for additional context
        
        Returns:
            Formatted text
        """
        lines = []
        
        # Header
        lines.append(f"=== {finding.get('problem_type', 'Unknown Problem').replace('_', ' ').title()} ===")
        lines.append("")
        
        # Article and citation info
        lines.append(f"Article: {finding.get('wikipedia_article', 'Unknown')}")
        if citation and citation.get('citation_number'):
            lines.append(f"Citation #{citation['citation_number']}")
        if citation and citation.get('source_title'):
            lines.append(f"Source: {citation['source_title']}")
        lines.append("")
        
        # Problem details
        lines.append("Problem:")
        lines.append(finding.get('details', 'No details available'))
        lines.append("")
        
        # Severity
        severity = finding.get('severity', 'medium')
        severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
        lines.append(f"Severity: {severity_emoji} {severity.title()}")
        lines.append("")
        
        # Dates
        found_date = finding.get('found_date')
        if found_date:
            if isinstance(found_date, str):
                found_date = datetime.fromisoformat(found_date.replace('Z', '+00:00'))
            lines.append(f"Found: {found_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Status
        status = finding.get('reporting_status', 'pending')
        lines.append(f"Status: {status}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_wikipedia_alert(finding: Dict[str, Any], citation: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a finding as a Wikipedia Talk page alert.
        
        Args:
            finding: Finding dictionary from database
            citation: Optional citation dictionary for additional context
        
        Returns:
            Wikipedia markup formatted alert
        """
        lines = []
        
        # Header
        lines.append("== Citation Alert ==")
        lines.append("{{WikiVerify alert}}")
        lines.append("")
        
        # Main message
        citation_num = citation.get('citation_number', 'X') if citation else 'X'
        article = finding.get('wikipedia_article', 'this article')
        lines.append(f"Citation [{citation_num}] in {article} may have an issue:")
        lines.append("")
        
        # Problem details
        problem_type = finding.get('problem_type', 'unknown').replace('_', ' ').title()
        lines.append(f"'''Problem''': {problem_type}")
        lines.append("")
        
        if citation and citation.get('source_title'):
            lines.append(f"'''Source''': {citation['source_title']}")
            lines.append("")
        
        # Details
        details = finding.get('details', 'No details available')
        lines.append(f"'''Details''': {details}")
        lines.append("")
        
        # Archive link if available
        if citation and citation.get('snapshot_url'):
            lines.append(f"[Archived version available|{citation['snapshot_url']}]")
            lines.append("")
        
        # Footer
        lines.append("This is an automated message. ~~~~")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_summary(findings: List[Dict[str, Any]]) -> str:
        """
        Format a summary of multiple findings.
        
        Args:
            findings: List of finding dictionaries
        
        Returns:
            Formatted summary text
        """
        if not findings:
            return "No findings to report."
        
        lines = []
        lines.append(f"=== WikiVerify Summary ===")
        lines.append("")
        lines.append(f"Total findings: {len(findings)}")
        lines.append("")
        
        # Group by problem type
        by_type = {}
        for finding in findings:
            problem_type = finding.get('problem_type', 'unknown')
            if problem_type not in by_type:
                by_type[problem_type] = []
            by_type[problem_type].append(finding)
        
        # Summary by type
        for problem_type, type_findings in by_type.items():
            lines.append(f"{problem_type.replace('_', ' ').title()}: {len(type_findings)}")
        
        lines.append("")
        lines.append("=== Details ===")
        lines.append("")
        
        # List each finding
        for i, finding in enumerate(findings, 1):
            lines.append(f"--- Finding {i} ---")
            lines.append(FindingFormatter.format_finding(finding))
            lines.append("")
        
        return "\n".join(lines)
