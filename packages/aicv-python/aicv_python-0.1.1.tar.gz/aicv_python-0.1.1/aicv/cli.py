"""
AiCV Python SDK CLI

Command-line interface for the AiCV SDK.
"""

import argparse
import sys
from typing import Optional
from .client import AiCVClient
from .exceptions import AiCVError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AiCV Python SDK - AI-powered CV analysis and generation"
    )
    
    parser.add_argument(
        "--api-key",
        required=True,
        help="Your AiCV API key"
    )
    
    parser.add_argument(
        "--base-url",
        default="https://api.aicv.com",
        help="Base URL for the API (default: https://api.aicv.com)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a CV")
    analyze_parser.add_argument("--cv-text", required=True, help="CV text to analyze")
    analyze_parser.add_argument(
        "--analysis-type",
        choices=["comprehensive", "skills", "experience"],
        default="comprehensive",
        help="Type of analysis to perform"
    )
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate CV content")
    generate_parser.add_argument("--section-type", required=True, help="Type of section to generate")
    generate_parser.add_argument("--context", required=True, help="Context for generation")
    generate_parser.add_argument("--requirements", help="Specific requirements")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Optimize a CV")
    optimize_parser.add_argument("--cv-text", required=True, help="CV text to optimize")
    optimize_parser.add_argument("--target-job", help="Target job description")
    
    # Account command
    account_parser = subparsers.add_parser("account", help="Get account information")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check API health")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = AiCVClient(api_key=args.api_key, base_url=args.base_url)
        
        if args.command == "analyze":
            result = client.analyze_cv(args.cv_text, args.analysis_type)
            print("Analysis Result:")
            print(result)
            
        elif args.command == "generate":
            result = client.generate_cv_section(
                args.section_type,
                args.context,
                args.requirements
            )
            print("Generated Content:")
            print(result)
            
        elif args.command == "optimize":
            result = client.optimize_cv(args.cv_text, args.target_job)
            print("Optimization Suggestions:")
            print(result)
            
        elif args.command == "account":
            result = client.get_account_info()
            print("Account Information:")
            print(result)
            
        elif args.command == "health":
            result = client.health_check()
            print("API Health Status:")
            print(result)
            
    except AiCVError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    main()
