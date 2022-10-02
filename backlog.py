import json
import pprint
from urllib import error
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)


class BacklogAPI:
    def __init__(self, api_key:str, space_name:str ="openhouse", domain="jp",project_id:int =None, project_key:str =None, project_name:str =None)->any:
        self.api_key = api_key
        self.api_version = "v2"
        self.space_name = space_name
        self.domein = domain
        self.project = self.get_project(project_id if project_id else project_key if project_key else [project.get("id") for project in self.get_projects() if project.get("name")==project_name][0]) if project_id or project_key or project_name else dict()

    def send_request(self, method:str ="GET", endpoint:str =None, message:str ="リクエスト送信時にエラーが発生しました", **kwargs)->any:
        base_url = f"https://{self.space_name}.backlog.{self.domein}/api/{self.api_version}/"
        parameters = "".join([f"&{key}={json.dumps(val)}".replace('"', '') if type(val)!=list else "".join([f"&{key}[]={json.dumps(v)}" for v in val]) for key, val in kwargs.items() if val])
        url = f"{base_url}{endpoint}?apiKey={self.api_key}"
        url += parameters if method=="GET" else ""
        request = Request(url=url)
        if method!="GET":
            message = "更新項目が存在しないためエラーが発生しました。"
            url = f"{base_url}{endpoint}?apiKey={self.api_key}"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = urlencode({key if type(val)!=list else f"{key}[]" : val if type(val)!=list else val[0] for key, val in kwargs.items() if val}).encode("utf-8")
            request = Request(
                url=url,
                method=method,
                headers=headers,
                data=data,
            )
        try:
            return json.loads(urlopen(request).read()) if endpoint else None
        except error.HTTPError as e:
            print(e)
            raise CustomException(message)

    def response_filter(self, data:list, **kwargs):
        key = next(iter(kwargs))
        return list(filter(lambda d: d.get(key)==kwargs[key], data))[0]

    def get_projects(self, archived:bool =False, all:bool =False)->list:
        return self.send_request("GET", "projects", archived=archived, all=all)

    def get_project(self, project_id_or_key:str =None)->dict:
        return self.send_request("GET", f"projects/{project_id_or_key}")

    def get_issues(self, id:list =[], parent_issue_id:list =[], keyword:str =[], project_id:list =[], issue_type_id:list =[], category_id:list =[], version_id:list =[], milestone_id:list =[], status_id:list =[], priority_id:list =[], assignee_id:list =[], created_user_id:list =[], resolution_id:list =[], parent_child:int =None, attachment:bool =False, shared_file:bool =False, sort:str =None, order:str =None, offset:int =None, count:int =None, created_since:str =None, created_until:str =None, updated_since:str =None, updated_until:str =None, start_date_since:str =None, start_date_until:str =None, due_date_since:str =None, due_date_until:str =None) -> list:
        if not project_id:
            project_id = [self.project.get("id")] if self.project.get("id") else list()
        return self.send_request(
            "GET",
            "issues",
            id=id,
            parentIssueId=parent_issue_id,
            keyword=keyword,
            projectId=project_id,
            issueTypeId=issue_type_id,
            categoryId=category_id,
            versionId=version_id,
            milestoneId=milestone_id,
            statusId=status_id,
            priorityId=priority_id,
            assigneeId=assignee_id,
            createdUserId=created_user_id,
            resolutionId=resolution_id,
            parentChild=parent_child,
            attachment=attachment,
            sharedFile=shared_file,
            sort=sort,
            order=order,
            offset=offset,
            count=count,
            createdSince=created_since,
            createdUntil=created_until,
            updatedSince=updated_since,
            updatedUntil=updated_until,
            startDateSince=start_date_since,
            startDateUntil=start_date_until,
            dueDateSince=due_date_since,
            dueDateUntil=due_date_until,
        )

    def get_issue(self, issue_id_or_key:str)->dict:
        return self.send_request("GET", f"issues/{issue_id_or_key}")

    def set_issue(self, project_id:int, summary:str, issue_type_id:int, priority_id:int, parent_issue_id:int =None, description:str =None, start_date:str =None, due_date:str =None, estimated_hours:int =None, actual_hours:int =None, category_id:list =[], version_id:list =[], milestone_id:list =[], assignee_id:int =None, notified_user_id:list =[], attachment_id:list =[]):
        if not project_id:
            project_id = self.project.get("id")
        return self.send_request(
            "POST",
            f"issues",
            projectId=project_id,
            summary=summary,
            parentIssueId=parent_issue_id,
            description=description,
            startDate=start_date,
            dueDate=due_date,
            estimatedHours=estimated_hours,
            actualHours=actual_hours,
            issueTypeId=issue_type_id,
            categoryId=category_id,
            versionId=version_id,
            milestoneId=milestone_id,
            priorityId=priority_id,
            assigneeId=assignee_id,
            notifiedUserId=notified_user_id,
            attachmentId=attachment_id,
        )

    def update_issue(self, issue_id_or_key:str, summary:str =None, parent_issue_id:int =None, description:str =None, status_id:int =None, resolution_id:int =None, start_date:str =None, due_date:str =None, estimated_hours:int =None, actual_hours:int =None, issue_type_id:int =None, category_id:list =[], version_id:list =[], milestone_id:list =[], priority_id:int = None, assignee_id:int =None, notified_user_id:list =[], attachment_id:list =[], comment:str =None)->dict:
        return self.send_request(
            "PATCH",
            f"issues/{issue_id_or_key}",
            summary=summary,
            parentIssueId=parent_issue_id,
            description=description,
            statusId=status_id,
            resolutionId=resolution_id,
            startDate=start_date,
            dueDate=due_date,
            estimatedHours=estimated_hours,
            actualHours=actual_hours,
            issueTypeId=issue_type_id,
            categoryId=category_id,
            versionId=version_id,
            milestoneId=milestone_id,
            priorityId=priority_id,
            assigneeId=assignee_id,
            notifiedUserId=notified_user_id,
            attachmentId=attachment_id,
            comment=comment,
        )

    def get_categories(self, project_id_or_key:str =None)->list:
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.send_request("GET", f"projects/{project_id_or_key}/categories")

    def get_category(self, name:str, project_id_or_key:str =None)->dict:
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.response_filter(self.get_categories(project_id_or_key=project_id_or_key), name)

    def get_issue_types(self, project_id_or_key:str =None)->list:
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.send_request("GET", f"projects/{project_id_or_key}/issueTypes")

    def get_issue_type(self, name:str, project_id_or_key:str =None)->dict:
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.response_filter(self.get_issue_types(project_id_or_key=project_id_or_key), name=name)

    def get_statuses(self, project_id_or_key:str =None):
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.send_request("GET", f"projects/{project_id_or_key}/statuses")

    def get_statuse(self, name:str, project_id_or_key:str =None):
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.response_filter(self.send_request("GET", f"projects/{project_id_or_key}/statuses"), name=name)

    def get_versions(self, project_id_or_key:str =None)->list:
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.send_request("GET", f"projects/{project_id_or_key}/versions")

    def get_version(self, name:str, project_id_or_key:str =None)->dict:
        if not project_id_or_key:
            project_id_or_key = self.project.get("id")
        return self.response_filter(self.send_request("GET", f"projects/{project_id_or_key}/versions"), name=name)

    def set_versions(self, name:str, project_id:str =None, description:str =None, start_date:str =None, release_due_date:str =None)->dict:
        if not project_id:
            project_id = self.project.get("id")
        try:
            return self.send_request(
                "POST",
                f"projects/{project_id}/versions",
                name=name,
                description=description,
                startDate=start_date,
                releaseDueDate=release_due_date
            )
        except:
            return self.get_version(project_id_or_key=project_id, name=name)

    def create_or_update_release_note(self, parent_issue_id_or_key:str, release_version:str, pr_list:list, project_id:int =None, summary:str =None, issue_type_id:int =None, priority_id:int =None, parent_issue_id:int =None, description:str =None, start_date:str =None, due_date:str =None, estimated_hours:int =None, actual_hours:int =None, category_id:list =[], version_id:list =[], milestone_id:list =[], assignee_id:int =None, notified_user_id:list =[], attachment_id:list =[]):
        parent_issue = self.get_issue(issue_id_or_key=parent_issue_id_or_key)
        child_issues = self.get_issues(parent_issue_id=[parent_issue.get("id")])
        issue = list(filter(lambda child_issue: child_issue.get("versions")[0].get("name")==release_version, child_issues))
        if issue:
            return self.update_release_note(issue_id_or_key=issue[0].get("id"), pr_list=pr_list)
        check_status = backlog.get_statuse("dev確認済み")
        hotfix = list(filter(lambda child_issue: child_issue.get("status")!=check_status, child_issues))
        if hotfix:
            summary = f"Version {release_version}"
            version = self.set_versions(release_version)
            version_id = [version.get("id")]
            return self.update_release_note(issue_id_or_key=hotfix[0].get("id"), pr_list=pr_list, summary=summary, version_id=version_id, hotfix_flg=True)
        else:
            return self.create_release_note(
                parent_issue.get("id"),
                release_version,
                pr_list,
                project_id=project_id,
                summary=summary,
                issue_type_id=parent_issue.get("issueType").get("id"),
                priority_id=parent_issue.get("priority").get("id"),
                parent_issue_id=parent_issue_id,
                description=description,
                start_date=start_date,
                due_date=due_date,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours,
                category_id=category_id,
                version_id=version_id,
                milestone_id=milestone_id,
                assignee_id=assignee_id,
                notified_user_id=notified_user_id,
                attachment_id=attachment_id
            )

    def create_release_note(self, parent_issue_id_or_key:str, release_version:str, pr_list:list, project_id:int =None, summary:str =None, issue_type_id:int =None, priority_id:int =None, parent_issue_id:int =None, description:str =None, start_date:str =None, due_date:str =None, estimated_hours:int =None, actual_hours:int =None, category_id:list =[], version_id:list =[], milestone_id:list =[], assignee_id:int =None, notified_user_id:list =[], attachment_id:list =[]):
        parent_issue_id = parent_issue_id_or_key
        summary = f"Version {release_version}"
        version = self.set_versions(release_version)
        version_id = [version.get("id")]
        description = "*リリースノート\n**本番環境反映予定PR一覧\n" + "".join(list(map(lambda pr: f"- [ ] {pr}\n" ,pr_list)))
        return self.set_issue(project_id, summary, issue_type_id, priority_id, parent_issue_id, description, start_date, due_date, estimated_hours, actual_hours, category_id, version_id, milestone_id, assignee_id, notified_user_id, attachment_id)

    def update_release_note(self, issue_id_or_key:str, pr_list:list, summary:str =None, version_id:int =None, hotfix_flg:bool =False):
        issue = self.get_issue(issue_id_or_key)
        issue_description = issue.get("description")
        if hotfix_flg:
            previous_version = issue.get("versions")[0].get("name")
            pr_list = list(map(lambda pr: f"\n- [x] {pr}" ,pr_list))
            if "**本番環境反映済みHotFixPR一覧" in issue_description:
                new_description = "\n".join([line if line!="**本番環境反映予定PR一覧" else f"***Version {previous_version}"+"".join(pr_list)+f"\n{line}" for line in issue_description.split("\n")])
            else:
                new_description = "\n".join([line if line!="*リリースノート" else f"{line}"+"\n**本番環境反映済みHotFixPR一覧"+f"\n***Version {previous_version}"+"".join(pr_list) for line in issue_description.split("\n")])
        else:
            pr_list = list(map(lambda pr: f"\n- [ ] {pr}" ,pr_list))
            new_description = issue_description + "".join(pr_list)
        return self.update_issue(issue_id_or_key=issue_id_or_key, description=new_description, summary=summary, version_id=version_id)


backlog = BacklogAPI("nseVpOi4L3gbMhgTsCqgibPlNeYFxRKWeEyicvD5HmSAhS5qEhs2ZA9UNdSwvdPP", project_key="SAICHANN", space_name="saichann", domain="com")

# issue = backlog.get_issue(issue_id_or_key="SILVER-29")

pprint.pprint(
    backlog.create_or_update_release_note(
        parent_issue_id_or_key="SAICHANN-1",
        release_version="0.0.20", pr_list = [
            "SISHIN_DEVELOP-7274【インフラ】S-ishinの死活監視をプログラムをLambdaで構築",
            "SISHIN_DEVELOP-7274【インフラ】S-ishinの死活監視をプログラムをLambdaで構築",
            "SISHIN_DEVELOP-7274【インフラ】S-ishinの死活監視をプログラムをLambdaで構築"
        ]
    )
)
# pprint.pprint(backlog.get_issue_type(name="リリースノート"))
# new_description = issue.get("description") + "".join(list(map(lambda pr: f"- [ ] {pr}\n" ,pr_list)))
# pprint.pprint(backlog.update_release_note(issue_id_or_key="SILVER-29", description=new_description))

