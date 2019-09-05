update django_migrations set name='0001_profiles_initial' where app='profiles' and name='0001_initial';
update django_migrations set name='0001_core_initial' where app='core' and name='0001_initial';
update django_migrations set name='0001_oauth_initial' where app='oauth' and name='0001_initial';
update django_migrations set name='0001_table_initial' where app='table' and name='0001_initial';
update django_migrations set name='0001_scheduler_initial' where app='scheduler' and name='0001_initial';
update django_migrations set name='0001_dataops_initial' where app='dataops' and name='0001_initial';
update django_migrations set name='0001_logs_initial' where app='logs' and name='0001_initial';
update django_migrations set name='0001_action_initial' where app='action' and name='0001_initial';
update django_migrations set name='0001_workflow_initial' where app='workflow' and name='0001_initial';

update django_migrations set app='ontask' where app='profiles' or
app='core' or app='oauth' or app='table' or app='scheduler' or
app='dataops' or app='logs' or app='action' or app='workflow'
