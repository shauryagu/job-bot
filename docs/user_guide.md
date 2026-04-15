# User Guide

## Getting Started

Job Bot is your personal job application copilot that helps you find, apply, and track jobs while keeping you in control of every important decision.

### First-Time Setup

1. **Configure Your Profile**
   - Set up your personal information
   - Define your job preferences
   - Add your resume variants

2. **Create Company Watchlist**
   - Add target companies
   - Set priority levels
   - Define preferred locations

3. **Connect Google Sheets**
   - Create a spreadsheet with required tabs
   - Connect your Google account
   - Verify sync works

## Core Features

### 1. Job Discovery

#### Automatic Job Fetching
Job Bot automatically fetches jobs from your configured sources:
- Greenhouse
- Lever
- Ashby
- Manual company watchlists

#### Manual Job Fetching
Trigger a manual fetch anytime:
```bash
# Via API
POST /api/jobs/fetch

# Via script
python scripts/fetch_jobs.py
```

### 2. Job Review & Approval

#### Review New Jobs
1. Check the "New Jobs" queue
2. Review each job's details
3. Approve, reject, or save for later

#### Job Scoring
Jobs are automatically scored based on:
- **Fit Score** (1-5): How well the role matches your skills
- **Company Priority** (1-5): How much you want to work there
- **Freshness** (1-5): How recently the job was posted
- **Location Match** (0-3): NYC vs Remote vs Other
- **Referral Potential** (0-2): Whether you have connections
- **Effort Penalty** (0 to -3): How complex the application is

#### Action Buckets
Jobs are automatically categorized into:
- **Apply Now**: High priority, good fit
- **Apply Soon**: Good fit, moderate priority
- **Outreach First**: Good fit, but reach out first
- **Monitor**: Keep an eye on it
- **Skip**: Not a good fit

### 3. Application Assistance

#### Guided Application Flow
1. Select a job from your queue
2. Review the application packet
3. Launch browser automation
4. Auto-fill standard fields
5. Review and confirm submission

#### Auto-filled Fields
Job Bot automatically fills:
- Name and contact information
- Location
- LinkedIn and GitHub profiles
- Resume upload
- Common demographic questions (if configured)

#### Manual Review Required
Job Bot will pause for:
- Custom questions
- Long-form answers
- Ambiguous fields
- Anything uncertain

### 4. Tracker Management

#### Automatic Updates
After confirming submission, Job Bot automatically:
- Creates or updates tracker entry
- Sets application stage
- Creates follow-up tasks
- Syncs with Google Sheets

#### Manual Updates
Update application status anytime:
```bash
# Via API
PUT /api/applications/{id}/status

# Fields you can update:
# - stage: applied, screening, technical, onsite, offer, rejected
# - next_action: What to do next
# - follow_up_due: When to follow up
# - notes: Any additional notes
```

### 5. Outreach Support

#### Contact Discovery
Job Bot helps you find contacts:
- Recruiters
- Hiring managers
- Team members
- Alumni connections

#### Draft Generation
Generate personalized outreach drafts:
- Recruiter introductions
- Hiring manager notes
- Engineer insight requests
- Warm contact messages

#### Outreach Workflow
1. Select contact type
2. Generate draft
3. Personalize message
4. Send manually (never automatic)
5. Track response

### 6. Follow-up Management

#### Automatic Follow-up Reminders
Job Bot creates follow-up tasks based on:
- Cold applications: 5-7 business days
- Warm contacts: 1-3 days
- High-priority startups: Same day

#### Follow-up Rules
- One follow-up unless there's engagement
- Stop after second touch without reply
- Customize timing per company

## User Preferences

### Target Roles
Configure your preferred role types:
- Backend engineer
- Infrastructure engineer
- Platform engineer
- Systems/tooling engineer
- ML infrastructure / inference platform
- Selective full stack (backend-heavy)

### Location Preferences
Set your location priorities:
- New York based (highest priority)
- New York office
- Remote
- Other locations

### Company Preferences
Define what matters to you:
- Strong technical teams
- Product-driven companies
- Intentional builders
- NYC startups and comparable companies

### Avoid Roles
Specify roles to avoid:
- Pure QA
- Test-focused roles
- Frontend-heavy roles (unless special case)

## Best Practices

### Job Review
1. **Review daily**: Check new jobs regularly
2. **Be decisive**: Approve or reject quickly
3. **Update preferences**: Refine as you learn

### Applications
1. **Quality over quantity**: Focus on good-fit roles
2. **Customize strategically**: Tailor for high-priority roles
3. **Track everything**: Keep detailed notes

### Outreach
1. **Be genuine**: Personalize every message
2. **Respect boundaries**: Don't spam contacts
3. **Follow up appropriately**: Time your follow-ups well

### Follow-up
1. **Stay organized**: Keep track of all follow-ups
2. **Be persistent but polite**: Follow up, don't pester
3. **Learn from feedback**: Adjust approach based on responses

## Mobile Usage

### Mobile-Friendly Features
- Read and review job queue
- Approve/reject jobs
- Update tracker
- Copy outreach drafts
- Mark outreach sent
- Review follow-up tasks

### Recommended Mobile Actions
- Mark applications as submitted
- Update application stages
- Send outreach messages
- Set next actions
- Review follow-up reminders

## Troubleshooting

### Jobs Not Appearing
1. Check if sources are configured
2. Verify API keys are valid
3. Check fetch logs for errors
4. Try manual fetch

### Application Assistance Not Working
1. Verify Playwright is installed
2. Check browser compatibility
3. Review autofill settings
4. Check job posting URL

### Tracker Sync Issues
1. Verify Google Sheets credentials
2. Check spreadsheet permissions
3. Review sync logs
4. Test connection manually

### Outreach Drafts Not Generating
1. Check LLM API configuration
2. Verify contact information
3. Review prompt templates
4. Check API credits

## Tips & Tricks

### Efficiency Tips
1. **Batch process**: Review jobs in batches
2. **Use templates**: Create message templates
3. **Keyboard shortcuts**: Learn API shortcuts
4. **Automate reminders**: Set up follow-up alerts

### Quality Tips
1. **Research companies**: Before applying
2. **Custom thoughtfully**: For important roles
3. **Network strategically**: Build meaningful connections
4. **Track patterns**: Learn what works

### Organization Tips
1. **Use tags**: Organize jobs by category
2. **Color code**: Visual priority indicators
3. **Regular cleanup**: Archive old applications
4. **Backup data**: Regular tracker backups

## Advanced Features

### Custom Scoring
Adjust scoring weights to match your priorities:
- Increase fit score importance
- Prioritize specific companies
- Adjust location preferences
- Customize effort penalties

### Automated Workflows
Set up automated job fetching:
- Schedule regular fetches
- Auto-filter by criteria
- Auto-score new jobs
- Notify on high-priority roles

### Integrations
Connect with other tools:
- Calendar integration for interviews
- Email integration for confirmations
- CRM integration for contact management
- Analytics for conversion tracking

## Security & Privacy

### Your Data
- Personal data stored securely
- Resume and answers kept local
- No unnecessary logging
- Explicit consent for all actions

### Best Practices
1. **Use strong passwords**: For all accounts
2. **Enable 2FA**: Where available
3. **Review permissions**: Regularly
4. **Keep software updated**: Security patches

### What We Don't Do
- Automatic submissions
- Automatic messaging
- Aggressive scraping
- Data sharing without consent

## Getting Help

### Documentation
- API docs: `/docs`
- Architecture guide: `docs/architecture.md`
- Deployment guide: `docs/deployment.md`

### Support
- GitHub Issues: Report bugs and request features
- Community: Join discussions
- Email: Contact for support

### Resources
- Tutorial videos: Coming soon
- Blog posts: Tips and best practices
- Webinars: Live training sessions

## FAQ

**Q: Can Job Bot apply to jobs automatically?**
A: No. Job Bot requires your approval for every submission.

**Q: How often should I review new jobs?**
A: Daily is ideal, but at least 2-3 times per week.

**Q: Can I use Job Bot for multiple job searches?**
A: Currently designed for single user, but multi-user support is planned.

**Q: What if a job posting URL doesn't work?**
A: Report it via GitHub issues and we'll fix the fetcher.

**Q: Can I customize the scoring algorithm?**
A: Yes, you can adjust weights in the configuration.

**Q: Is my data secure?**
A: Yes. We use encryption, secure storage, and follow best practices.

**Q: Can I export my data?**
A: Yes, you can export tracker data anytime.

**Q: How do I add new job sources?**
A: Contact us or contribute a new fetcher.

**Q: What's the difference between Apply Now and Apply Soon?**
A: Apply Now is for high-priority, good-fit roles. Apply Soon is for good roles that can wait a bit.

**Q: Can I use Job Bot on my phone?**
A: Yes! The mobile interface supports all essential actions.