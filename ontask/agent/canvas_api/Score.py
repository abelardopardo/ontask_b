from .etc.conf import *
from .res import *

class Score(Res):
    def create(self, course_id, line_item_id, params={}):
        """
        Source Code:
            Code: Lti::Ims::ScoresController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/scores_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/scores.create
        
        Scope:
            url:POST|/api/lti/courses/:course_id/line_items/:line_item_id/scores

        
        Module: Score
        Function Description: Create a Score

        Parameter Desc:
            userId                                                                   |Required |string  |The lti_user_id or the Canvas user_id. Returns a 422 if user not found in Canvas or is not a student.
            activityProgress                                                         |Required |string  |Indicate to Canvas the status of the user towards the activity’s completion. Must be one of Initialized, Started, InProgress, Submitted, Completed.
            gradingProgress                                                          |Required |string  |Indicate to Canvas the status of the grading process. A value of PendingManual will require intervention by a grader. Values of NotReady, Failed, and Pending will cause the scoreGiven to be ignored. FullyGraded values will require no action. Possible values are NotReady, Failed, Pending, PendingManual, FullyGraded.
            timestamp                                                                |Required |string  |Date and time when the score was modified in the tool. Should use ISO8601-formatted date with subsecond precision. Returns a 400 if the timestamp is earlier than the updated_at time of the Result.
            scoreGiven                                                               |         |number  |The Current score received in the tool for this line item and user, scaled to the scoreMaximum
            scoreMaximum                                                             |         |number  |Maximum possible score for this result; it must be present if scoreGiven is present. Returns 412 if not present when scoreGiven is present.
            comment                                                                  |         |string  |Comment visible to the student about this score.
            https://canvas.instructure.com/lti/submission                            |         |Object  |(EXTENSION) Optional submission type and data. Fields listed below.
            https://canvas.instructure.com/lti/submission[new_submission]            |         |boolean |(EXTENSION field) flag to indicate that this is a new submission. Defaults to true unless submission_type is none.
            https://canvas.instructure.com/lti/submission[prioritize_non_tool_grade] |         |boolean |(EXTENSION field) flag to prevent a request from overwriting an existing grade for a submission. Defaults to false.
            https://canvas.instructure.com/lti/submission[submission_type]           |         |string  |(EXTENSION field) permissible values are: none, basic_lti_launch, online_text_entry, external_tool, online_upload, or online_url. Defaults to external_tool. Ignored if content_items are provided.
            https://canvas.instructure.com/lti/submission[submission_data]           |         |string  |(EXTENSION field) submission data (URL or body text). Only used for submission_types basic_lti_launch, online_text_entry, online_url. Ignored if content_items are provided.
            https://canvas.instructure.com/lti/submission[submitted_at]              |         |string  |(EXTENSION field) Date and time that the submission was originally created. Should use ISO8601-formatted date with subsecond precision. This should match the data and time that the original submission happened in Canvas.
            https://canvas.instructure.com/lti/submission[content_items]             |         |Array   |(EXTENSION field) Files that should be included with the submission. Each item should contain ‘type: file`, and a url pointing to the file. It can also contain a title, and an explicit MIME type if needed (otherwise, MIME type will be inferred from the title or url). If any items are present, submission_type will be online_upload.

        Request Example: 
            {
              "timestamp": "2017-04-16T18:54:36.736+00:00",
              "scoreGiven": 83,
              "scoreMaximum": 100,
              "comment": "This is exceptional work.",
              "activityProgress": "Completed",
              "gradingProgress": "FullyGraded",
              "userId": "5323497",
              "https://canvas.instructure.com/lti/submission": {
                "new_submission": true,
                "submission_type": "online_url",
                "submission_data": "https://instructure.com",
                "submitted_at": "2017-04-14T18:54:36.736+00:00",
                "content_items": [
                  {
                    "type": "file",
                    "url": "https://instructure.com/test_file.txt",
                    "title": "Submission File",
                    "media_type": "text/plain"
                  }
                ]
              }
            }

        Response Example: 
            {
              "resultUrl": "https://canvas.instructure.com/url/to/result",
              "https://canvas.instructure.com/lti/submission": {
                "content_items": [
                  {
                    "type": "file",
                    "url": "https://instructure.com/test_file.txt",
                    "title": "Submission File"
                    "progress": "https://canvas.instructure.com/url/to/progress"
                  }
            }
        """
        method = "POST"
        api = f'/api/lti/courses/{course_id}/line_items/{line_item_id}/scores'
        return self.request(method, api, params)
        