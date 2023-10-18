from .etc.conf import *
from .res import *

class Conversations(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: ConversationsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.index
        
        Scope:
            url:GET|/api/v1/conversations

        
        Module: Conversations
        Function Description: List conversations

        Parameter Desc:
            scope                        | |string  |When set, only return conversations of the specified type. For example, set to `unread` to return only conversations that haven’t been read. The default behavior is to return all non-archived conversations (i.e. read and unread).                                                     Allowed values: unread, starred, archived
            filter[]                     | |string  |When set, only return conversations for the specified courses, groups or users. The id should be prefixed with its type, e.g. `user_123` or `course_456`. Can be an array (by setting `filter[]`) or single value (by setting `filter`)
            filter_mode                  | |string  |When filter[] contains multiple filters, combine them with this mode, filtering conversations that at have at least all of the contexts (`and`) or at least one of the contexts (`or`)                                                     Allowed values: and, or, default or
            interleave_submissions       | |boolean |(Obsolete) Submissions are no longer linked to conversations. This parameter is ignored.
            include_all_conversation_ids | |boolean |Default is false. If true, the top-level element of the response will be an object rather than an array, and will have the keys `conversations` which will contain the paged conversation data, and `conversation_ids` which will contain the ids of all conversations under this scope/filter in the same order.
            include[]                    | |string  |`participant_avatars`                                                     Optionally include an `avatar_url` key for each user participanting in the conversation                                                     Allowed values: participant_avatars

        Response Example: 
            [
              {
                "id": 2,
                "subject": "conversations api example",
                "workflow_state": "unread",
                "last_message": "sure thing, here's the file",
                "last_message_at": "2011-09-02T12:00:00Z",
                "message_count": 2,
                "subscribed": true,
                "private": true,
                "starred": false,
                "properties": ["attachments"],
                "audience": [2],
                "audience_contexts": {"courses": {"1": ["StudentEnrollment"]}, "groups": {}},
                "avatar_url": "https://canvas.instructure.com/images/messages/avatar-group-50.png",
                "participants": [
                  {"id": 1, "name": "Joe", "full_name": "Joe TA"},
                  {"id": 2, "name": "Jane", "full_name": "Jane Teacher"}
                ],
                "visible": true,
                "context_name": "Canvas 101"
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/conversations'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: ConversationsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.create
        
        Scope:
            url:POST|/api/v1/conversations

        
        Module: Conversations
        Function Description: Create a conversation

        Parameter Desc:
            recipients[]       |Required |string  |An array of recipient ids. These may be user ids or course/group ids prefixed with `course_` or `group_` respectively, e.g. recipients[]=1&recipients=2&recipients[]=course_3. If the course/group has over 100 enrollments, ‘bulk_message’ and ‘group_conversation’ must be set to true.
            subject            |         |string  |The subject of the conversation. This is ignored when reusing a conversation. Maximum length is 255 characters.
            body               |Required |string  |The message to be sent
            force_new          |         |boolean |Forces a new message to be created, even if there is an existing private conversation.
            group_conversation |         |boolean |Defaults to false.  When false, individual private conversations will be created with each recipient. If true, this will be a group conversation (i.e. all recipients may see all messages and replies). Must be set true if the number of recipients is over the set maximum (default is 100).
            attachment_ids[]   |         |string  |An array of attachments ids. These must be files that have been previously uploaded to the sender’s `conversation attachments` folder.
            media_comment_id   |         |string  |Media comment id of an audio or video file to be associated with this message.
            media_comment_type |         |string  |Type of the associated media file                                                   Allowed values: audio, video
            user_note          |         |boolean |Will add a faculty journal entry for each recipient as long as the user making the api call has permission, the recipient is a student and faculty journals are enabled in the account.
            mode               |         |string  |Determines whether the messages will be created/sent synchronously or asynchronously. Defaults to sync, and this option is ignored if this is a group conversation or there is just one recipient (i.e. it must be a bulk private message). When sent async, the response will be an empty array (batch status can be queried via the batches API)                                                   Allowed values: sync, async
            scope              |         |string  |Used when generating `visible` in the API response. See the explanation under the index API action                                                   Allowed values: unread, starred, archived
            filter[]           |         |string  |Used when generating `visible` in the API response. See the explanation under the index API action
            filter_mode        |         |string  |Used when generating `visible` in the API response. See the explanation under the index API action                                                   Allowed values: and, or, default or
            context_code       |         |string  |The course or group that is the context for this conversation. Same format as courses or groups in the recipients argument.
        """
        method = "POST"
        api = f'/api/v1/conversations'
        return self.request(method, api, params)
        
    def batches(self, params={}):
        """
        Source Code:
            Code: ConversationsController#batches,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.batches
        
        Scope:
            url:GET|/api/v1/conversations/batches

        
        Module: Conversations
        Function Description: Get running batches


        Response Example: 
            [
              {
                "id": 1,
                "subject": "conversations api example",
                "workflow_state": "created",
                "completion": 0.1234,
                "tags": [],
                "message":
                {
                  "id": 1,
                  "created_at": "2011-09-02T10:00:00Z",
                  "body": "quick reminder, no class tomorrow",
                  "author_id": 1,
                  "generated": false,
                  "media_comment": null,
                  "forwarded_messages": [],
                  "attachments": []
                }
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/conversations/batches'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: ConversationsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.show
        
        Scope:
            url:GET|/api/v1/conversations/:id

        
        Module: Conversations
        Function Description: Get a single conversation

        Parameter Desc:
            interleave_submissions | |boolean |(Obsolete) Submissions are no longer linked to conversations. This parameter is ignored.
            scope                  | |string  |Used when generating `visible` in the API response. See the explanation under the index API action                                               Allowed values: unread, starred, archived
            filter[]               | |string  |Used when generating `visible` in the API response. See the explanation under the index API action
            filter_mode            | |string  |Used when generating `visible` in the API response. See the explanation under the index API action                                               Allowed values: and, or, default or
            auto_mark_as_read      | |boolean |Default true. If true, unread conversations will be automatically marked as read. This will default to false in a future API release, so clients should explicitly send true if that is the desired behavior.

        Response Example: 
            {
              "id": 2,
              "subject": "conversations api example",
              "workflow_state": "unread",
              "last_message": "sure thing, here's the file",
              "last_message_at": "2011-09-02T12:00:00-06:00",
              "message_count": 2,
              "subscribed": true,
              "private": true,
              "starred": false,
              "properties": ["attachments"],
              "audience": [2],
              "audience_contexts": {"courses": {"1": []}, "groups": {}},
              "avatar_url": "https://canvas.instructure.com/images/messages/avatar-50.png",
              "participants": [
                {"id": 1, "name": "Joe", "full_name": "Joe TA"},
                {"id": 2, "name": "Jane", "full_name": "Jane Teacher"},
                {"id": 3, "name": "Bob", "full_name": "Bob Student"}
              ],
              "messages":
                [
                  {
                    "id": 3,
                    "created_at": "2011-09-02T12:00:00Z",
                    "body": "sure thing, here's the file",
                    "author_id": 2,
                    "generated": false,
                    "media_comment": null,
                    "forwarded_messages": [],
                    "attachments": [{"id": 1, "display_name": "notes.doc", "uuid": "abcdefabcdefabcdefabcdefabcdef"}]
                  },
                  {
                    "id": 2,
                    "created_at": "2011-09-02T11:00:00Z",
                    "body": "hey, bob didn't get the notes. do you have a copy i can give him?",
                    "author_id": 2,
                    "generated": false,
                    "media_comment": null,
                    "forwarded_messages":
                      [
                        {
                          "id": 1,
                          "created_at": "2011-09-02T10:00:00Z",
                          "body": "can i get a copy of the notes? i was out",
                          "author_id": 3,
                          "generated": false,
                          "media_comment": null,
                          "forwarded_messages": [],
                          "attachments": []
                        }
                      ],
                    "attachments": []
                  }
                ],
              "submissions": []
            }
        """
        method = "GET"
        api = f'/api/v1/conversations/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: ConversationsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.update
        
        Scope:
            url:PUT|/api/v1/conversations/:id

        
        Module: Conversations
        Function Description: Edit a conversation

        Parameter Desc:
            conversation[workflow_state] | |string  |Change the state of this conversation                                                     Allowed values: read, unread, archived
            conversation[subscribed]     | |boolean |Toggle the current user’s subscription to the conversation (only valid for group conversations). If unsubscribed, the user will still have access to the latest messages, but the conversation won’t be automatically flagged as unread, nor will it jump to the top of the inbox.
            conversation[starred]        | |boolean |Toggle the starred state of the current user’s view of the conversation.
            scope                        | |string  |Used when generating `visible` in the API response. See the explanation under the index API action                                                     Allowed values: unread, starred, archived
            filter[]                     | |string  |Used when generating `visible` in the API response. See the explanation under the index API action
            filter_mode                  | |string  |Used when generating `visible` in the API response. See the explanation under the index API action                                                     Allowed values: and, or, default or

        Response Example: 
            {
              "id": 2,
              "subject": "conversations api example",
              "workflow_state": "read",
              "last_message": "sure thing, here's the file",
              "last_message_at": "2011-09-02T12:00:00-06:00",
              "message_count": 2,
              "subscribed": true,
              "private": true,
              "starred": false,
              "properties": ["attachments"],
              "audience": [2],
              "audience_contexts": {"courses": {"1": []}, "groups": {}},
              "avatar_url": "https://canvas.instructure.com/images/messages/avatar-50.png",
              "participants": [{"id": 1, "name": "Joe", "full_name": "Joe TA"}]
            }
        """
        method = "PUT"
        api = f'/api/v1/conversations/{id}'
        return self.request(method, api, params)
        
    def mark_all_as_read(self, params={}):
        """
        Source Code:
            Code: ConversationsController#mark_all_as_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.mark_all_as_read
        
        Scope:
            url:POST|/api/v1/conversations/mark_all_as_read

        
        Module: Conversations
        Function Description: Mark all as read

        """
        method = "POST"
        api = f'/api/v1/conversations/mark_all_as_read'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: ConversationsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.destroy
        
        Scope:
            url:DELETE|/api/v1/conversations/:id

        
        Module: Conversations
        Function Description: Delete a conversation


        Response Example: 
            {
              "id": 2,
              "subject": "conversations api example",
              "workflow_state": "read",
              "last_message": null,
              "last_message_at": null,
              "message_count": 0,
              "subscribed": true,
              "private": true,
              "starred": false,
              "properties": []
            }
        """
        method = "DELETE"
        api = f'/api/v1/conversations/{id}'
        return self.request(method, api, params)
        
    def add_recipients(self, id, params={}):
        """
        Source Code:
            Code: ConversationsController#add_recipients,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.add_recipients
        
        Scope:
            url:POST|/api/v1/conversations/:id/add_recipients

        
        Module: Conversations
        Function Description: Add recipients

        Parameter Desc:
            recipients[] |Required |string |An array of recipient ids. These may be user ids or course/group ids prefixed with `course_` or `group_` respectively, e.g. recipients[]=1&recipients=2&recipients[]=course_3

        Response Example: 
            {
              "id": 2,
              "subject": "conversations api example",
              "workflow_state": "read",
              "last_message": "let's talk this over with jim",
              "last_message_at": "2011-09-02T12:00:00-06:00",
              "message_count": 2,
              "subscribed": true,
              "private": false,
              "starred": null,
              "properties": [],
              "audience": [2, 3, 4],
              "audience_contexts": {"courses": {"1": []}, "groups": {}},
              "avatar_url": "https://canvas.instructure.com/images/messages/avatar-group-50.png",
              "participants": [
                {"id": 1, "name": "Joe", "full_name": "Joe TA"},
                {"id": 2, "name": "Jane", "full_name": "Jane Teacher"},
                {"id": 3, "name": "Bob", "full_name": "Bob Student"},
                {"id": 4, "name": "Jim", "full_name": "Jim Admin"}
              ],
              "messages":
                [
                  {
                    "id": 4,
                    "created_at": "2011-09-02T12:10:00Z",
                    "body": "Jim was added to the conversation by Joe TA",
                    "author_id": 1,
                    "generated": true,
                    "media_comment": null,
                    "forwarded_messages": [],
                    "attachments": []
                  }
                ]
            }
        """
        method = "POST"
        api = f'/api/v1/conversations/{id}/add_recipients'
        return self.request(method, api, params)
        
    def add_message(self, id, params={}):
        """
        Source Code:
            Code: ConversationsController#add_message,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.add_message
        
        Scope:
            url:POST|/api/v1/conversations/:id/add_message

        
        Module: Conversations
        Function Description: Add a message

        Parameter Desc:
            body                |Required |string  |The message to be sent.
            attachment_ids[]    |         |string  |An array of attachments ids. These must be files that have been previously uploaded to the sender’s `conversation attachments` folder.
            media_comment_id    |         |string  |Media comment id of an audio of video file to be associated with this message.
            media_comment_type  |         |string  |Type of the associated media file.                                                    Allowed values: audio, video
            recipients[]        |         |string  |no description
            included_messages[] |         |string  |no description
            user_note           |         |boolean |Will add a faculty journal entry for each recipient as long as the user making the api call has permission, the recipient is a student and faculty journals are enabled in the account.

        Response Example: 
            {
              "id": 2,
              "subject": "conversations api example",
              "workflow_state": "unread",
              "last_message": "let's talk this over with jim",
              "last_message_at": "2011-09-02T12:00:00-06:00",
              "message_count": 2,
              "subscribed": true,
              "private": false,
              "starred": null,
              "properties": [],
              "audience": [2, 3],
              "audience_contexts": {"courses": {"1": []}, "groups": {}},
              "avatar_url": "https://canvas.instructure.com/images/messages/avatar-group-50.png",
              "participants": [
                {"id": 1, "name": "Joe", "full_name": "Joe TA"},
                {"id": 2, "name": "Jane", "full_name": "Jane Teacher"},
                {"id": 3, "name": "Bob", "full_name": "Bob Student"}
              ],
              "messages":
                [
                  {
                    "id": 3,
                    "created_at": "2011-09-02T12:00:00Z",
                    "body": "let's talk this over with jim",
                    "author_id": 2,
                    "generated": false,
                    "media_comment": null,
                    "forwarded_messages": [],
                    "attachments": []
                  }
                ]
            }
        """
        method = "POST"
        api = f'/api/v1/conversations/{id}/add_message'
        return self.request(method, api, params)
        
    def remove_messages(self, id, params={}):
        """
        Source Code:
            Code: ConversationsController#remove_messages,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.remove_messages
        
        Scope:
            url:POST|/api/v1/conversations/:id/remove_messages

        
        Module: Conversations
        Function Description: Delete a message

        Parameter Desc:
            remove[] |Required |string |Array of message ids to be deleted

        Response Example: 
            {
              "id": 2,
              "subject": "conversations api example",
              "workflow_state": "read",
              "last_message": "sure thing, here's the file",
              "last_message_at": "2011-09-02T12:00:00-06:00",
              "message_count": 1,
              "subscribed": true,
              "private": true,
              "starred": null,
              "properties": ["attachments"]
            }
        """
        method = "POST"
        api = f'/api/v1/conversations/{id}/remove_messages'
        return self.request(method, api, params)
        
    def batch_update(self, params={}):
        """
        Source Code:
            Code: ConversationsController#batch_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.batch_update
        
        Scope:
            url:PUT|/api/v1/conversations

        
        Module: Conversations
        Function Description: Batch update conversations

        Parameter Desc:
            conversation_ids[] |Required |string |List of conversations to update. Limited to 500 conversations.
            event              |Required |string |The action to take on each conversation.                                                  Allowed values: mark_as_read, mark_as_unread, star, unstar, archive, destroy
        """
        method = "PUT"
        api = f'/api/v1/conversations'
        return self.request(method, api, params)
        
    def find_recipients(self, params={}):
        """
        Source Code:
            Code: ConversationsController#find_recipients,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.find_recipients
        
        Scope:
            url:GET|/api/v1/conversations/find_recipients

        
        Module: Conversations
        Function Description: Find recipients

        """
        method = "GET"
        api = f'/api/v1/conversations/find_recipients'
        return self.request(method, api, params)
        
    def unread_count(self, params={}):
        """
        Source Code:
            Code: ConversationsController#unread_count,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conversations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conversations.unread_count
        
        Scope:
            url:GET|/api/v1/conversations/unread_count

        
        Module: Conversations
        Function Description: Unread count


        Response Example: 
            {'unread_count': '7'}
        """
        method = "GET"
        api = f'/api/v1/conversations/unread_count'
        return self.request(method, api, params)
        