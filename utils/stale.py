# Copyright 2022 The HuggingFace Team, the AllenNLP library authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Script to close stale issue. Taken in part from the AllenNLP repository.
https://github.com/allenai/allennlp.
"""
from datetime import datetime as dt
import os

from github import Github


LABELS_TO_EXEMPT = [
    "good first issue",
    "feature request",
    "wip",
]


def main():
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo("huggingface/accelerate")
    open_issues = repo.get_issues(state="open")

    for issue in open_issues:
        comments = sorted(
            list(issue.get_comments()),
            key=lambda i: i.created_at,
            reverse=True,
        )

        last_comment = comments[0] if len(comments) > 0 else None
        current_time = dt.utcnow()
        days_since_updated = (current_time - issue.updated_at).days
        days_since_creation = (current_time - issue.created_at).days
        if (
            last_comment is not None
            and last_comment.user.login == "github-actions[bot]"
            and days_since_updated > 7
            and days_since_creation >= 30
            and all(
                label.name.lower() not in LABELS_TO_EXEMPT
                for label in issue.get_labels()
            )
        ):
            # Close issue since it has been 7 days of inactivity since bot mention.
            issue.edit(state="closed")
        elif (
            days_since_updated > 23
            and days_since_creation >= 30
            and all(
                label.name.lower() not in LABELS_TO_EXEMPT
                for label in issue.get_labels()
            )
        ):
            # Add stale comment
            issue.create_comment(
                "This issue has been automatically marked as stale because it has not had "
                "recent activity. If you think this still needs to be addressed "
                "please comment on this thread.\n\nPlease note that issues that do not follow the "
                "[contributing guidelines](https://github.com/huggingface/accelerate/blob/main/CONTRIBUTING.md) "
                "are likely to be ignored."
            )


if __name__ == "__main__":
    main()
