import os
from datetime import datetime


def get_updated_issues(redmine_url, api_key):
    from redminelib import Redmine
    redmine = Redmine(redmine_url, key=api_key)

    today = datetime.today()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        issues = redmine.issue.filter(
            updated_on=f'><{start_date.strftime('%Y-%m-%d')}',
            updated_by='me')

        user = redmine.user.get('current')

        issue_dicts = []
        for issue in issues:
            issue = redmine.issue.get(issue.id, include=['journals'])
            if not issue or not issue.journals:
                continue
            isOk = False
            for journal in issue.journals:
                if journal.created_on > start_date:
                    if journal.user.id == user.id:
                        isOk = True
                        break
            if not isOk:
                continue
            issue_dict = {
                'id': issue.id,
                'subject': issue.subject,
                'status': issue.status.name,
                'priority': issue.priority.name,
                'author': issue.author.name,
                'assigned_to': issue.assigned_to.name if issue.assigned_to else '',
                'start_date': issue.start_date.strftime('%Y-%m-%d') if issue.start_date else '',
                'due_date': issue.due_date.strftime('%Y-%m-%d') if issue.due_date else '',
                'done_ratio': issue.done_ratio,
                'created_on': issue.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_on': issue.updated_on.strftime('%Y-%m-%d %H:%M:%S'),
                'description': issue.description,
                'url': f'{redmine_url}/issues/{issue.id}',
            }
            issue_dicts.append(issue_dict)
    except Exception as e:
        return False, [str(e)]
    return True, issue_dicts


def main(args):
    if len(args) < 2:
        return 'Usage: value_redmine_issue.py <redmine-url> <redmine-api-key> <redmine-user-name>'
    redmine_url = args[0]
    access_key = args[1]
    if not access_key:
        from dotenv import load_dotenv
        load_dotenv()
        access_key = os.getenv('REDMINE_ACCESS_KEY')
    format = f'#{{id}}: {{subject}}'
    if len(args) > 2:
        format = args[2]
    is_ok, issues = get_updated_issues(redmine_url, access_key)
    if not is_ok:
        return issues[0]
    result = ''
    for issue in issues:
        if result:
            result += '\n'
        result += format.replace('{{', '{').replace('}}', '}').format(**issue)
    return result
