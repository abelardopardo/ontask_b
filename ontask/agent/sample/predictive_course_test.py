import sys
import os
sys.path.append(os.path.abspath(".."))
from canvas_api.etc import conf
from canvas_api import C3L
import json
from canvas_api import c3l_utils
import random as rd

class course_creator:
    def __init__(self, path):
        self.__path__ = path
        self.url_base = conf.api_base
        self.token = conf.wanhy149_token
        self.c3l_obj = C3L(conf.api_base, conf.wanhy149_token)
        self.user_id = 1
        #self.user_id = 'wanhy149@mymail.unisa.edu.au'
        self.__course_id_filename__ = 'course_id'
    
    def __destory_course__(self):
        if os.path.exists(self.__course_id_filename__):
            with open(self.__course_id_filename__, 'r') as fr:
                line = fr.readline()
                if len(line.strip()) > 0:
                    self.c3l_obj.courses.destroy(int(line), {'event': 'delete'})
    
    def __record_course_id__(self, course_id):
        with open(self.__course_id_filename__, 'w') as fw:
            fw.write(str(course_id))
    
    def create_course(self, user_id):
        course_obj = None
        ret = None
        file_name = f'{self.__path__ }/course.json'
        if not os.path.exists(file_name):
            return ret
        with open(file_name, 'r') as fr:
            course_obj = json.loads(fr.read())
        if course_obj:
            course_obj['course[name]'] = f'Predictive Analytics Auto_{rd.randint(1, 10)}'
            course_obj['course[code]'] = c3l_utils.get_unique_key()
            course_obj['course[sis_course_id]'] = c3l_utils.get_unique_key()
            course_obj['course[integration_id]'] = c3l_utils.get_unique_key()
            ret = self.c3l_obj.courses.create(user_id, course_obj)
        if ret:
            ret = json.loads(ret)
            if ret.__contains__('id'):
                self.__course_id__ = ret['id']
                self.__record_course_id__(ret['id'])
        return ret
    
    def create_modules(self, course_id):
        modules_obj = None
        for parent, _, files in os.walk(os.path.join(self.__path__, 'modules')):
            for file in files:
                modules_obj = None
                print(os.path.join(parent, file))
                with open(os.path.join(parent, file), 'r') as fr:
                    modules_obj = json.loads(fr.read())
                    if modules_obj:
                        self.c3l_obj.modules.create(course_id, modules_obj)
    
    def create_assignments(self, course_id):
        obj = None
        for parent, _, files in os.walk(os.path.join(self.__path__, 'assignments')):
            for file in files:
                obj = None
                print(os.path.join(parent, file))
                with open(os.path.join(parent, file), 'r') as fr:
                    obj = json.loads(fr.read())
                    if obj:
                        self.c3l_obj.assignments.create(course_id, obj)

    def create_quizze_questions(self, quiz_path, course_id, quiz_id):
        quiz_questions = filter(
            lambda x : x.startswith('quizze_q') and x.endswith('.json') and os.path.isfile(os.path.join(quiz_path, x)), 
            os.listdir(quiz_path)
        )
        quiz_questions = map(lambda x :  os.path.join(quiz_path, x), quiz_questions)
        for question in quiz_questions:
            question_obj= None
            with open(question, 'r', encoding='utf-8') as fr:
                print(question)
                question_obj = json.loads(fr.read())
                self.c3l_obj.quizquestions.create(course_id, quiz_id, question_obj)
        pass

    def create_quizze(self, course_id):
        obj = None
        quizzes_path = os.path.join(self.__path__, 'quizzes')
        quizzes_folders = filter(
            lambda x : os.path.isdir(x), 
            map(lambda item: os.path.join(quizzes_path, item), os.listdir(quizzes_path))
        )
        for quiz_path in quizzes_folders:
            print(quiz_path)
            if os.path.exists(os.path.join(quiz_path, 'quizze.json')):
                quiz_obj = None
                with open(os.path.join(quiz_path, 'quizze.json'), 'r') as fr:
                    quiz_obj = json.loads(fr.read())
                if quiz_obj:
                    quiz_ret = self.c3l_obj.quizzes.create(course_id, quiz_obj)
                    if quiz_ret:
                        quiz_ret = json.loads(quiz_ret)
                        print(quiz_ret)
                        if quiz_ret.__contains__('id'):
                            self.create_quizze_questions(quiz_path, course_id, quiz_ret['id'])
        #os.listdir("")
        #for parent, _, files in os.walk(os.path.join(self.__path__, 'quizzes')):
        #    for file in files:
        #        obj = None
        #        print(os.path.join(parent, file))
        #        with open(os.path.join(parent, file), 'r') as fr:
        #            obj = json.loads(fr.read())
        #            if obj:
        #                self.c3l_obj.assignments.create(course_id, obj)



    def create_quizze_question(self, course_id, quiz_id):
        for i in range(1, 2):
            question_obj = None
            with open(f'./data/quizze1_q{i}.json', 'r') as fr:
                question_obj = json.loads(fr.read())
            try:
                ret = self.c3l_obj.quizquestions.create(course_id, quiz_id, question_obj)
                #print(ret)
            except Exception as e:
                print(e)
                pass
    
    def create_pages(self, course_id):
        ret = []
        for parent, folders, files in os.walk(f"{self.__path__}/pages/"):
            for file in files:
                if file.lower().endswith(".json", ):
                    print(os.path.join(parent, file))
                    with open(os.path.join(parent, file), 'r', encoding="utf-8") as fr:
                        page_obj = json.loads(fr.read())
                        if os.path.exists(os.path.join(parent, file + ".txt")):
                            with open(os.path.join(parent, file + ".txt"), 'r', encoding="utf-8") as fr:
                                page_obj['wiki_page[body]'] = fr.read()
                        ret.append(self.c3l_obj.pages.create(course_id, page_obj))
        return ret

    def run(self):
        #print(self.c3l_obj.accounts.index())
        self.__destory_course__()
        
        course_obj = self.create_course(self.user_id)
        if course_obj:
            if course_obj.__contains__('name'):
                print(f'create course successful. {course_obj["name"]}  : id: {course_obj["id"]}' )

        if course_obj:
            self.create_pages(course_obj['id'])
            self.create_modules(course_obj['id'])
            self.create_assignments(course_obj['id'])
            self.create_quizze(course_obj['id'])
            #print(course_obj['id'], course_obj['name'])
            #self.c3l_obj.assignmentgroups.create()
    
if __name__ == '__main__':
    course_creator("./data/PredictiveAnalysis/").run()
    #obj = c3l_obj = C3L(conf.api_base, conf.wanhy149_token)
    #print(obj.accounts.courses_api(1))
    #print(obj.courses.index())
    #print(obj.courses.copy_course_content(164, {}))
    #print(obj.pages.index(164))


