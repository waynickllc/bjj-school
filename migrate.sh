#!/bin/bash
# Database Migration Helper Script
# This script provides shortcuts for common Flask-Migrate operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Flask app reference
FLASK_APP="run:app"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment is activated
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not activated. Activating..."
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
        elif [[ -f ".venv/bin/activate" ]]; then
            source .venv/bin/activate
        else
            print_error "Virtual environment not found. Please create one first."
            exit 1
        fi
    fi
}

# Show usage
usage() {
    cat << EOF
Database Migration Helper Script

Usage: ./migrate.sh [command]

Commands:
    init        Initialize migrations (first time setup)
    migrate     Create a new migration from model changes
    upgrade     Apply all pending migrations
    downgrade   Revert last migration
    current     Show current migration version
    history     Show migration history
    stamp       Mark database as being at a specific revision
    reset       Reset database (WARNING: destroys all data)
    help        Show this help message

Examples:
    ./migrate.sh migrate "Add email_verified field"
    ./migrate.sh upgrade
    ./migrate.sh downgrade
    ./migrate.sh current

EOF
}

# Initialize migrations
cmd_init() {
    print_info "Initializing Flask-Migrate..."
    flask --app "$FLASK_APP" db init
    print_info "Migrations initialized successfully!"
}

# Create new migration
cmd_migrate() {
    local message="$1"
    if [[ -z "$message" ]]; then
        print_error "Migration message required"
        echo "Usage: ./migrate.sh migrate \"Description of changes\""
        exit 1
    fi
    
    print_info "Creating new migration: $message"
    flask --app "$FLASK_APP" db migrate -m "$message"
    print_info "Migration created successfully!"
    print_warning "Please review the generated migration file before applying it."
}

# Apply migrations
cmd_upgrade() {
    print_info "Applying pending migrations..."
    flask --app "$FLASK_APP" db upgrade
    print_info "Migrations applied successfully!"
}

# Revert migration
cmd_downgrade() {
    print_warning "Reverting last migration..."
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        flask --app "$FLASK_APP" db downgrade
        print_info "Migration reverted successfully!"
    else
        print_info "Downgrade cancelled."
    fi
}

# Show current version
cmd_current() {
    print_info "Current migration version:"
    flask --app "$FLASK_APP" db current
}

# Show history
cmd_history() {
    print_info "Migration history:"
    flask --app "$FLASK_APP" db history
}

# Stamp database
cmd_stamp() {
    local revision="${1:-head}"
    print_info "Stamping database at revision: $revision"
    flask --app "$FLASK_APP" db stamp "$revision"
    print_info "Database stamped successfully!"
}

# Reset database (dangerous!)
cmd_reset() {
    print_error "WARNING: This will destroy all data in the database!"
    read -p "Are you absolutely sure? Type 'yes' to confirm: " -r
    echo
    if [[ $REPLY == "yes" ]]; then
        print_warning "Resetting database..."
        
        # Read database config from config.yaml
        DB_NAME=$(grep -A 5 "^database:" config.yaml | grep "name:" | awk '{print $2}')
        DB_USER=$(grep -A 5 "^database:" config.yaml | grep "user:" | awk '{print $2}')
        
        print_info "Dropping and recreating database: $DB_NAME"
        mysql -u "$DB_USER" -p -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        
        print_info "Applying migrations..."
        flask --app "$FLASK_APP" db upgrade
        
        print_info "Database reset complete!"
    else
        print_info "Reset cancelled."
    fi
}

# Main script
main() {
    check_venv
    
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        init)
            cmd_init
            ;;
        migrate)
            cmd_migrate "$@"
            ;;
        upgrade)
            cmd_upgrade
            ;;
        downgrade)
            cmd_downgrade
            ;;
        current)
            cmd_current
            ;;
        history)
            cmd_history
            ;;
        stamp)
            cmd_stamp "$@"
            ;;
        reset)
            cmd_reset
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
