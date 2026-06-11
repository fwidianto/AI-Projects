"""
AI Job Intelligence Platform - MVP Main Entry Point

CLI application for job discovery, scoring, and reporting.

Usage:
    python main.py --search "ERP Analyst"
    python main.py --scrape
    python main.py --report
    python main.py --all
"""

import argparse
import sys
from pathlib import Path

# Add mvp to path
sys.path.insert(0, str(Path(__file__).parent))

from mvp.config_loader import load_config
from mvp.database import Database
from mvp.scraper import IndeedScraper, create_sample_jobs
from mvp.scoring import JobScorer
from mvp.export import export_jobs_to_csv, export_summary_csv, export_profile_csv
from mvp.report import generate_text_report, generate_html_report, generate_markdown_report


def setup_database(db_path: str = "data/jobs.db") -> Database:
    """Initialize and return database instance."""
    print(f"📁 Initializing database: {db_path}")
    return Database(db_path)


def load_profile(config_path: str = "config/profile.json"):
    """Load user profile from config."""
    print(f"📋 Loading profile from: {config_path}")
    try:
        config = load_config(config_path)
        print(f"✅ Profile loaded: {config.profile.name}")
        print(f"   Target roles: {len(config.profile.target_roles)}")
        print(f"   Skills: {len(config.profile.skills)}")
        return config
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Run 'python main.py --setup' to create sample config")
        sys.exit(1)


def scrape_jobs(args, config):
    """Scrape jobs from Indeed."""
    print("\n" + "=" * 60)
    print("🔍 SCRAPING JOBS")
    print("=" * 60)
    
    db = setup_database(args.db)
    
    if args.use_sample:
        print("📦 Using sample jobs (no scraping)")
        jobs = create_sample_jobs()
    else:
        print(f"🌐 Scraping from Indeed...")
        scraper = IndeedScraper(rate_limit=args.rate_limit)
        
        all_jobs = []
        for query in config.profile.target_roles[:3]:  # Limit to top 3 roles
            print(f"   Searching: {query}")
            result = scraper.search(
                query=query,
                location=args.location or config.search_preferences.default_location,
                max_results=args.max_results,
                days_back=args.days,
            )
            
            if result.success:
                print(f"   ✅ Found {len(result.jobs)} jobs")
                all_jobs.extend(result.jobs)
            else:
                print(f"   ❌ Error: {result.error}")
    
    # Store jobs in database
    if jobs:
        print(f"\n💾 Storing {len(jobs)} jobs in database...")
        count = db.insert_jobs_batch(jobs)
        print(f"✅ Stored {count} new jobs")
    else:
        print("⚠️ No jobs to store")
    
    return db


def score_jobs(args, config, db):
    """Score jobs against profile."""
    print("\n" + "=" * 60)
    print("📊 SCORING JOBS")
    print("=" * 60)
    
    # Get all jobs from database
    jobs = db.get_all_jobs(limit=1000)
    print(f"📋 Found {len(jobs)} jobs in database")
    
    if not jobs:
        print("⚠️ No jobs to score. Run --scrape first.")
        return []
    
    # Initialize scorer
    scorer = JobScorer(config.profile, config.scoring_weights)
    
    # Score all jobs
    print("🎯 Scoring jobs against your profile...")
    results = scorer.score_jobs(jobs)
    
    # Store scores
    scored_count = 0
    for result in results:
        db.insert_score(result.score)
        scored_count += 1
    
    print(f"✅ Scored {scored_count} jobs")
    
    # Show top matches
    print("\n🏆 TOP 5 MATCHES:")
    print("-" * 60)
    for rank, result in enumerate(results[:5], 1):
        job = result.job
        score = result.score
        print(f"{rank}. {job.title}")
        print(f"   {job.company} | {job.location or 'N/A'}")
        print(f"   Match: {score.total_score:.1f}% ({score.score_label})")
        print()
    
    return results


def generate_reports(args, config, results):
    """Generate reports."""
    print("\n" + "=" * 60)
    print("📄 GENERATING REPORTS")
    print("=" * 60)
    
    if not results:
        print("⚠️ No scored jobs. Run --score first.")
        return
    
    # Generate reports
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Text report
    txt_path = output_dir / "job_report.txt"
    path = generate_text_report(results, config.profile, str(txt_path))
    print(f"✅ Text report: {path}")
    
    # HTML report
    html_path = output_dir / "job_report.html"
    path = generate_html_report(results, config.profile, str(html_path))
    print(f"✅ HTML report: {path}")
    
    # Markdown report
    md_path = output_dir / "job_report.md"
    path = generate_markdown_report(results, config.profile, str(md_path))
    print(f"✅ Markdown report: {path}")
    
    # CSV export
    csv_path = output_dir / "jobs_export.csv"
    path = export_jobs_to_csv(results, str(csv_path))
    print(f"✅ CSV export: {path}")
    
    # Summary CSV
    summary_path = output_dir / "jobs_summary.csv"
    path = export_summary_csv(results, str(summary_path))
    print(f"✅ Summary CSV: {path}")


def show_stats(args, config):
    """Show database statistics."""
    print("\n" + "=" * 60)
    print("📈 DATABASE STATISTICS")
    print("=" * 60)
    
    db = setup_database(args.db)
    stats = db.get_stats()
    
    print(f"\n📊 Jobs Overview:")
    print(f"   Total Jobs: {stats['total_jobs']}")
    print(f"   Scored Jobs: {stats['scored_jobs']}")
    print(f"   Applied Jobs: {stats['applied_jobs']}")
    
    if stats.get("by_source"):
        print(f"\n📍 By Source:")
        for source in stats["by_source"]:
            print(f"   {source['source']}: {source['count']}")
    
    if stats.get("score_distribution"):
        print(f"\n📊 Score Distribution:")
        for dist in stats["score_distribution"]:
            print(f"   {dist['range']}: {dist['count']}")


def show_profile(args, config):
    """Show profile information."""
    print("\n" + "=" * 60)
    print("👤 YOUR PROFILE")
    print("=" * 60)
    
    profile = config.profile
    
    print(f"\n📋 Name: {profile.name}")
    print(f"📝 Headline: {profile.headline or 'N/A'}")
    print(f"💼 Experience: {profile.experience_years} years")
    
    print(f"\n🎯 Target Roles:")
    for role in profile.target_roles:
        print(f"   - {role}")
    
    print(f"\n📍 Preferred Locations:")
    for loc in profile.preferred_locations:
        print(f"   - {loc}")
    
    print(f"\n💰 Salary Expectations:")
    sal = profile.salary_expectations
    print(f"   {sal.min/1_000_000:.0f}M - {sal.max/1_000_000:.0f}M {sal.currency}")
    
    print(f"\n🛠️ Skills ({len(profile.skills)}):")
    for skill in profile.skills[:10]:
        key = "⭐" if skill.is_key_skill else "  "
        print(f"   {key} {skill.name} (proficiency: {skill.proficiency})")
    
    if len(profile.skills) > 10:
        print(f"   ... and {len(profile.skills) - 10} more")


def setup_sample_data(args):
    """Create sample config and database."""
    print("\n" + "=" * 60)
    print("🔧 SETUP SAMPLE DATA")
    print("=" * 60)
    
    # Create directories
    Path("config").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Sample config already exists, just inform
    if Path("config/profile.json").exists():
        print("✅ Sample profile already exists: config/profile.json")
    else:
        print("📝 Copy config/profile.json to customize your profile")
    
    # Initialize database with sample jobs
    db = Database("data/jobs.db")
    jobs = create_sample_jobs()
    count = db.insert_jobs_batch(jobs)
    print(f"✅ Added {count} sample jobs to database")
    
    print("\n📝 Next steps:")
    print("   1. Edit config/profile.json with your details")
    print("   2. Run 'python main.py --all' to scrape, score, and report")
    print("   3. Or run individual commands:")
    print("      python main.py --scrape --use-sample  # Use sample data")
    print("      python main.py --score               # Score jobs")
    print("      python main.py --report              # Generate reports")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Job Intelligence Platform - MVP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --setup              Setup sample data
  python main.py --scrape             Scrape jobs from Indeed
  python main.py --scrape --use-sample  Use sample jobs (no scraping)
  python main.py --score              Score all jobs against profile
  python main.py --report             Generate reports
  python main.py --all                Run full pipeline
  python main.py --stats              Show database statistics
  python main.py --profile            Show profile details
        """
    )
    
    parser.add_argument(
        "--config",
        default="config/profile.json",
        help="Path to profile config file (default: config/profile.json)"
    )
    parser.add_argument(
        "--db",
        default="data/jobs.db",
        help="Path to SQLite database (default: data/jobs.db)"
    )
    
    # Action arguments
    parser.add_argument("--setup", action="store_true", help="Setup sample data")
    parser.add_argument("--scrape", action="store_true", help="Scrape jobs")
    parser.add_argument("--score", action="store_true", help="Score jobs")
    parser.add_argument("--report", action="store_true", help="Generate reports")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--profile", action="store_true", help="Show profile")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    
    # Scraper options
    parser.add_argument("--use-sample", action="store_true", help="Use sample jobs instead of scraping")
    parser.add_argument("--location", default=None, help="Job location filter")
    parser.add_argument("--max-results", type=int, default=50, help="Max results per query")
    parser.add_argument("--days", type=int, default=30, help="Days back to search")
    parser.add_argument("--rate-limit", type=float, default=2.0, help="Seconds between requests")
    
    args = parser.parse_args()
    
    # Default action: show help
    if not any([args.setup, args.scrape, args.score, args.report, args.stats, args.profile, args.all]):
        parser.print_help()
        print("\n💡 Tip: Use --all to run the full pipeline")
        return
    
    # Load config
    config = load_profile(args.config)
    
    # Execute actions
    results = []
    
    if args.setup:
        setup_sample_data(args)
    
    if args.all or args.scrape:
        db = scrape_jobs(args, config)
    
    if args.all or args.score:
        if not args.all:
            db = setup_database(args.db)
        score_results = score_jobs(args, config, db)
        results = score_results
    
    if args.report:
        generate_reports(args, config, results)
    
    if args.stats:
        show_stats(args, config)
    
    if args.profile:
        show_profile(args, config)
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()