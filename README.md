# OnTask: Personalised feedback at scale

Current Version: 2.5.0 ([documentation](http://ontask-version-b.readthedocs.io/en/latest/))

## OnTask in a nutshell

- Authentication through LTI, LDAP, Shibboleth

- Data upload through CSV or Excel files

- Actions such as personalised email, personalised web page

- Integrated annotation capture mechanism (similar to a survey engine)

- Email tracking integrated in data table

- Workflows shareable with other users (for teams of instructors)

- Time-based scheduler for actions

- Import/Export functionality to share workflows and data.

- Table views to see only a subset of the data

**For a detailed description of the tool, how to install it, and how to use it
check the [OnTask Documentation](https://abelardopardo.github.io/ontask_b)**.

## OnTask FAQ

Welcome to OnTask, the platform offering teachers and educational designers
the capacity to use data to personalise the experience for the learners. For 
a detailed description of what is OnTask, how to install it and use it, read
the [OnTask Documentation](https://abelardopardo.github.io/ontask_b).

Here is a quick summary about ontask:

Q1. **What is it?** A web tool that allows instructors and learners to connect 
    data collected during a learning experience with the use of basic rules 
    (*if this then that*) to personalise support actions.
  
Q2. **What kind of data?** OnTask assumes there exist data related to how 
    learners interact while participating in a learning experience. This can be
    obtained through a Learning Management System, collected by hand, through 
    surveys, etc. OnTask allows you to upload the data, it stores it in a table
    in which every row contains information about one student, and use
    that data to then personalise how learners see certain resources or receive
    certain information (these are what we call the *actions*).

Q3. **Does OnTask collect the data for me?** In its basic form, no. It assumes 
    that you have access to the data yourself and offers a simple way to upload
    it into the platform to be then used to deploy *actions*. If you you have 
    specific needs to obtain data, let us know and we can discuss other options.
     
Q4. **For which courses is OnTask most useful?** OnTask is ideal for courses 
    with a large number of students, in which it makes sense to contact the 
    students either through email or providing them regular suggestions, and 
    for which there is data available to decide how to personalise such 
    suggestions. These emails or suggestions are called *actions* within OnTask
    and can be easily created with different elements depending on the student 
    data available. 
   
Q5. **What is an action?** In OnTask, an action is the process
    of either providing (*action out*) or requesting (*action in*) information 
    to/from learners. An action out 
    can be an email to the learner with text that is personalised based on 
    the collected data, or a web page with content selected based on this same 
    data. An *action in* is page requesting information from the students (like
    a simple survey) that can then be used to personalise the *actions out*.
  
Q6. **But how is this personalisation done?** Simple. OnTask allows you to 
    write simple rules that decide if a portion of text in an email or a web 
    page appears or not based on the available data. For example, you may 
    choose to write two different blurbs for those learners that passed and 
    failed a set of questions in an exam. Or different suggestions for those 
    that are minimally, partially, or completely engaged with the course 
    activities (although you need data about this!). 
    Theses rules are then applied to every learner to obtain the personalised 
    text (or resource). This is particularly useful when you have a large 
    student cohort and want to provide some level of personalisation at a 
    reasonable effort. 

Q7. **If I send these personalised emails, how do I know if they are used?** 
    OnTask will help you track that information and add it automatically to the
    data table.
   
Q8. **And what if I want to know which email was sent to which student?** Every
    time you send emails OnTask offers you the possibility of storing a 
    *snapshot* of your workflow. You can save that file and upload it as 
    another workflow in the platform to simply browse through the emails that 
    were sent.
     
Q9. **Will OnTask help me collect information such as attendance?** Yes. This 
    is a case of an **action in**. OnTask simplifies the task of defining the 
    type of information that needs to be collected and then offer instructors a
    simple way to enter that information as it is captured.
  
Q10. **How about collecting information such as student annotations?** Yes. As 
     in the case of attendance, OnTask allows you to pre-define the type of 
     information you would like to annotate and then quickly select a student 
     and enter the required data.  

Q12. **How about if I want the learners to enter their own annotations?** Yes. 
     OnTask offers a URL through which (authenticated) learners provide their 
     own annotations. This can serve as a simple *survey engine* with the data
     ready for you to use to personalise actions.

Q13. **What if I have a team of instructors?** No problem. OnTask bundles all 
     the information related to a course in a *workflow*. The creator of a 
     workflow can then share it with other OnTask users that will have access 
     to a subset of the operations.
  
Q14. **Nice, but sometimes you only want to see a subset of the data**. No 
     problem. OnTask allows you to define *views* of the data by selecting a 
     subset of rows and columns. You can simply set up these views for the 
     different instructors, so that they only have to deal with the data 
     relevant to them.

Q15. **After a course finishes, there seems to be quite a lot of information
     and intelligence captured in OnTask. How do I reuse it?** Easy. OnTask
     offers you the possibility of exporting and importing your data so you 
     can either archive it for future reference or share your actions, rules,
     views, etc with other user.
  
Q16. **Can I use OnTask with my institutional authentication?** Yes. OnTaks 
     comes with the basic functionality to be compatible with the most common 
     authentication mechanisms such as LTI, LDAP, Shibboleth, etc.
  
Q17. **How are these emails sent?** OnTask offers the functionality to connect 
     to an SMTP server so that emails are sent to the learners. This connection 
     may need specific parameters to make sure the emails are delivered properly
     and are not mistaken by span.
  
Q18. **This seems like a complex tool to install** OnTask is a web platform and 
     as such, it needs some basic infrastructure to execute (a machine to keep 
     the server running, proper authentication, connection with a SMTP server, 
     etc.) You can deploy the tool in your own personal computer, but it will 
     have restricted functionality.
  
Q19. **Where do I find the details on how to install it and some more 
     information?** Check the [OnTask Documentation](https://abelardopardo.github.io/ontask_b).   
     
## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## Credits

OnTask started as a project combining ideas that were present in the Student 
Relationship Engagement System [SRES](http://sres.io) and subsequent versions. 
Support for this activity has been provided by the Australian Government 
Office for Learning and Teaching as part of the [OnTask Project](https://ontasklearning.org) 
titled *Scaling the Provision of Personalised Learning Support Actions to
Large Student Cohorts* (OLT project reference SP16-5264). The views expressed
in this activity do not necessarily reflect the views of the Australian
Government Office for Learning and Teaching. 
 
## License

MIT License

Copyright (c) 2017 Office for Learning and Teaching. Australian Government

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Other applications distributed as part of OnTask

- [django-auth-lti package](https://github.com/Harvard-University-iCommons/django-auth-lti). 
  The package has been modified to use email as sole authentication field, and
  to prevent the patching of the `reverse` method in Django.

- [django-datetime-widget](https://github.com/asaglimbeni/django-datetime-widget) BSD

- [django-summernote](https://github.com/summernote/django-summernote) MIT

- [jQuery QueryBuilder](http://querybuilder.js.org/) MIT

- [searchable-option-list](https://github.com/pbauerochse/searchable-option-list) MIT

## Additional libraries used by OnTask

OnTask uses the following additional libraries/modules with the following 
licenses:

- [coreapi](https://pypi.python.org/pypi/coreapi) BSD

- [Django](https://www.djangoproject.com) BSD License

- [django-admin-bootstrapped](https://github.com/django-admin-bootstrapped/django-admin-bootstrapped) Apache 2.0

- [django-authtools](https://github.com/fusionbox/django-authtools) BSD

- [django-braces](https://pypi.python.org/pypi/django-braces/1.12.0). BSD 
  License

- [django-crispy-forms](https://pypi.python.org/pypi/django-crispy-forms/1.7.0) 
  MIT

- [django-environ](https://pypi.python.org/pypi/django-environ) MIT License

- [django-extensions](https://github.com/django-extensions/django-extensions)
  MIT

- [django-import-export](https://github.com/django-import-export/django-import-export) BSD

- [django-jquery](https://pypi.python.org/pypi/django-jquery/3.1.0) BSD

- [django-redis](https://github.com/niwinz/django-redis) BSD

- [django-siteprefs](https://github.com/idlesign/django-siteprefs), BSD

- [django-tables2](https://github.com/jieter/django-tables2) MIT

- [django-widget-tweaks](https://github.com/jazzband/django-widget-tweaks) MIT

- [djangorestframework](https://pypi.python.org/pypi/djangorestframework/3.7.7) 
  BSD

- [easy-thumbnails](https://pypi.python.org/pypi/easy-thumbnails) BSD

- [ims-lti-py](https://github.com/tophatmonocle/ims_lti_py) MIT

- [Markdown](https://pypi.python.org/pypi/Markdown) BSD

- [mock](https://pypi.python.org/pypi/mock) BSD

- [oauth2](https://github.com/joestump/python-oauth2) MIT

- [pandas](https://pandas.pydata.org/) BSD

- [psycopg2](https://pypi.python.org/pypi/psycopg2) LGPL with exceptions or ZPL

- [Pygments](https://pypi.python.org/pypi/Pygments) BSD

- [Python](https://python.org) Python Software Foundation License

- [python-ldap](https://bitbucket.org/psagers/django-auth-ldap/) BSD

- [pytz](https://pypi.python.org/pypi/pytz) MIT

- [Redis](https://redis.io) BSD

- [Sphinx](https://pypi.python.org/pypi/Sphinx) BSD

- [SQLAlchemy](https://pypi.python.org/pypi/SQLAlchemy/1.2.0) MIT

- [tzlocal](https://pypi.python.org/pypi/tzlocal) MIT

- [validate_email](https://pypi.python.org/pypi/validate_email) LGPL

