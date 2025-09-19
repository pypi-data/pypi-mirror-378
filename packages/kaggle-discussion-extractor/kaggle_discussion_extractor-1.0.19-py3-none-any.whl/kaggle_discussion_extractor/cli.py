#!/usr/bin/env python3
"""
Command Line Interface for Kaggle Discussion Extractor
"""

import argparse
import asyncio
import sys
from pathlib import Path
from .core import KaggleDiscussionExtractor
from .notebook_downloader import KaggleNotebookDownloader


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Extract discussions from Kaggle competitions with hierarchical reply structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all discussions from a competition
  %(prog)s https://www.kaggle.com/competitions/neurips-2025
  
  # Extract only 10 discussions
  %(prog)s https://www.kaggle.com/competitions/neurips-2025 --limit 10
  
  # Enable development mode for detailed logging
  %(prog)s https://www.kaggle.com/competitions/neurips-2025 --dev-mode
  
  # Run with visible browser (non-headless)
  %(prog)s https://www.kaggle.com/competitions/neurips-2025 --no-headless
        """
    )
    
    parser.add_argument(
        'competition_url',
        help='URL of the Kaggle competition to extract discussions from'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit the number of discussions to extract (default: extract all)'
    )
    
    parser.add_argument(
        '--dev-mode', '-d',
        action='store_true',
        help='Enable development mode with detailed logging'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (not headless)'
    )

    parser.add_argument(
        '--writeups', '-w',
        action='store_true',
        help='Extract writeups from competition leaderboard'
    )

    parser.add_argument(
        '--notebooks', '-n',
        action='store_true',
        help='Download and convert competition notebooks to Python files'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='kaggle-discussion-extractor 1.0.17'
    )
    
    return parser


async def main():
    """Main CLI function"""
    parser = create_parser()
    args = parser.parse_args()

    # Validate competition URL
    if not args.competition_url.startswith('https://www.kaggle.com/competitions/'):
        print("Error: Please provide a valid Kaggle competition URL")
        print("Example: https://www.kaggle.com/competitions/neurips-2025")
        sys.exit(1)

    # Initialize extractor
    extractor = KaggleDiscussionExtractor(
        dev_mode=args.dev_mode,
        headless=not args.no_headless
    )

    print("=" * 60)
    print("Kaggle Discussion Extractor")
    print("=" * 60)
    print(f"Competition: {args.competition_url}")
    print("Features:")
    print("  - Hierarchical reply extraction (1, 1.1, 1.2, etc.)")
    print("  - No content duplication between parent/child replies")
    print("  - Pagination support for all discussions")
    print("  - Rich metadata extraction (rankings, badges, upvotes)")
    print("  - Clean markdown output")

    if args.dev_mode:
        print("  - Development mode: ENABLED")
    if args.no_headless:
        print("  - Browser mode: VISIBLE")

    print()

    try:
        success = False
        results = []

        # Check what to extract
        if args.writeups:
            # Extract writeups
            print("Starting writeup extraction...")
            writeup_success = await extractor.extract_competition_writeups(
                competition_url=args.competition_url,
                limit=args.limit
            )
            results.append(("WRITEUP", writeup_success))

        if args.notebooks:
            # Extract notebooks
            print("Starting notebook extraction...")
            notebook_downloader = KaggleNotebookDownloader(
                dev_mode=args.dev_mode,
                headless=not args.no_headless
            )

            notebook_success = await notebook_downloader.download_competition_notebooks(
                competition_url=args.competition_url,
                limit=args.limit
            )
            results.append(("NOTEBOOK", notebook_success))

        if not args.writeups and not args.notebooks:
            # Extract discussions (default)
            print("Starting discussion extraction...")
            discussion_success = await extractor.extract_competition_discussions(
                competition_url=args.competition_url,
                limit=args.limit
            )
            results.append(("DISCUSSION", discussion_success))

        # Print results
        print("\n" + "=" * 60)
        if results:
            all_success = all(result[1] for result in results)
            for feature, result in results:
                status = "SUCCESS" if result else "FAILED"
                print(f"{feature} EXTRACTION: {status}")

                if feature == "DISCUSSION" and result:
                    print("  -> Check 'kaggle_discussions_extracted' directory")
                elif feature == "WRITEUP" and result:
                    print("  -> Check 'kaggle_writeups_extracted' directory")
                elif feature == "NOTEBOOK" and result:
                    print("  -> Check 'kaggle_notebooks_downloaded' directory")

            if all_success:
                print("\nALL EXTRACTIONS COMPLETED SUCCESSFULLY!")
            else:
                print("\nSOME EXTRACTIONS FAILED - check error messages above")

            success = all_success
        else:
            print("NO EXTRACTION PERFORMED")
            success = False

        print("=" * 60)
        return success

    except KeyboardInterrupt:
        print("\nExtraction cancelled by user")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if args.dev_mode:
            import traceback
            traceback.print_exc()
        return False


def cli_main():
    """Entry point for console script"""
    # Handle version first (non-async)
    parser = create_parser()

    # Pre-check for version to avoid async issues
    if len(sys.argv) > 1 and sys.argv[1] in ['--version', '-v']:
        print('kaggle-discussion-extractor 1.0.17')
        return

    try:
        # Use asyncio.run() with proper exception handling
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nExtraction cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli_main()