# OnTask: Personalised feedback at scale

Welcome to OnTask, the platform offering teachers and educational designers
the capacity to use data to personalise the experience for the learners.

Learning is complex, highly situated, and requires interacting with peers,
instructors, resources, platforms, etc. This complexity can be alleaviated
providing learners with the right support actions. But this process becomes
increasingly complex when the number of learners grows. The more learners,
the more difficult is for instructors to provide support and the usual
solution is to provide generic resources that are only relevant to a subset
of the audience (think reminder about upcoming assessment deadline).

In parallel wih this increase in complexity, learning platforms now generate
a wealth of data about those interactions that are technology mediated. This
data can be collected and used to help instructors and designers to provide a
truly personalised experience. Why is this not hapenning in current
platforms? Because the connection between this data and learner support
actions is very challenging to implement. This is the focus of OnTask:
provide instructors and designers with a platform to connect data emerging
from learning environments with highly personalised student support actions.

Why OnTask? There are several platforms out there that implement similar
functionality, and the common thread is the positive impact that personalised
communication may have when supporting learners. There are a few scientific
publications that document the ideas and processes that inspired the creation
of OnTask:

- Liu, D. Y.-T., Taylor, C. E., Bridgeman, A. J., Bartimote-Aufflick, K., & Pardo, A. (2016). Empowering instructors through customizable collection and analyses of actionable information Workshop on Learning Analytics for Curriculum and Program Quality Improvement (pp. 3). Edinburgh, UK.
- Liu, D. Y. T., Bartimote-Aufflick, K., Pardo, A., & Bridgeman, A. J. (2017). Data-driven Personalization of Student Learning Support in Higher Education. In A. Peña-Ayala (Ed.), Learning analytics: Fundaments, applications, and trends: A view of the current state of the art: Springer.  doi:10.1007/978-3-319-52977-6_5
- Pardo, A., Jovanović, J., Dawson, S., Gašević, D., & Mirriahi, N. (In press). Using Learning Analytics to Scale the Provision of Personalised Feedback. British Journal of Educational Technology. doi:10.1111/bjet.12592

## Installation

Check the section [Installation Process](https://github.com/abelardopardo/ontask_b/blob/master/docs/Install/index.rst) in the documentation.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## Credits

OnTask has been developed as part of the [OnTask Project](https://ontasklearning.org) titled *Scaling the Provision of Personalised Learning Support Actions to Large Student Cohorts* and supported by the Office for Leanring and Teaching of the Australian Government.

OnTask uses a modified version of the [django-auth-lti package](https://github.com/Harvard-University-iCommons/django-auth-lti). See its [LICENSE](https://github.com/Harvard-University-iCommons/django-auth-lti/blob/master/LICENSE) for details. The package has been modified to use email as sole authentication field, and to prevent the patching of the ``reverse`` methond in Django.
 
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
