# calculating the median in days from self-removal TD
library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
postgresql <- dbSendQuery(con, "select epoch_time_to_remove from processed_comments where has_removed_version = true and introduced_version_author = removed_version_author")
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
median(data1$epoch_time_to_remove/86400)


# calculating the median in days from non self-removal TD
library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
postgresql <- dbSendQuery(con, "select epoch_time_to_remove from processed_comments where has_removed_version = true and introduced_version_author != removed_version_author")
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
median(data1$epoch_time_to_remove/86400)


# self-removal histogram
library(RPostgreSQL)
library(vioplot)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
postgresql <- dbSendQuery(con, "select 'Apache-Abdera' as project_name, epoch_time_to_remove from processed_comments where has_removed_version = true and introduced_version_author = removed_version_author")
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
# hist(data1$epoch_time_to_remove/86400, xlab='Days to remove', main = paste('Self-removal histogram of ', data1$project_name[1]) )
vioplot(data1$epoch_time_to_remove/86400, names=c(data1$project_name[1]),   col="gold")
title(paste('Self-removal of ', data1$project_name[1]), ylab="Number of days")


# non self-removal histogram
library(RPostgreSQL)
library(vioplot)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
postgresql <- dbSendQuery(con, "select 'Apache-Abdera' as project_name, epoch_time_to_remove from processed_comments where has_removed_version = true and introduced_version_author != removed_version_author")
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
# hist(data1$epoch_time_to_remove/86400, xlab='Days to remove', main = paste('Non self-removal histogran of ', data1$project_name[1]) )
vioplot(data1$epoch_time_to_remove/86400, names=c(data1$project_name[1]),   col="gold")
title(paste('Non self-removal of ', data1$project_name[1]), ylab="Number of days")

# calculating the median in days for different types of td
library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
# postgresql <- dbSendQuery(con, "select epoch_time_to_remove from processed_comments where has_removed_version = true and td_classification = 'DESIGN' ")
postgresql <- dbSendQuery(con, "select epoch_time_to_remove from processed_comments where has_removed_version = true and td_classification =  'REQUIREMENT' ")

data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
median(data1$epoch_time_to_remove/86400)

# Different types of TD violin plot
library(RPostgreSQL)
library(vioplot)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
# postgresql <- dbSendQuery(con, "select 'Design Debt' as comment_classification, 'Apache-Abdera' as project_name, epoch_time_to_remove from processed_comments  where has_removed_version = true and td_classification = 'DESIGN' ")
postgresql <- dbSendQuery(con, "select 'Requirement Debt' as comment_classification, 'Apache-Abdera' as project_name, epoch_time_to_remove from processed_comments where  has_removed_version = true and td_classification = 'REQUIREMENT' ")

data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
# hist(data1$epoch_time_to_remove/86400, xlab='Days to remove', main = paste('Histogram of ', data1$comment_classification[1]))
vioplot(data1$epoch_time_to_remove/86400, names=c(data1$comment_classification[1]),   col="gold")
# , ylim = c(500,3500)
title(paste(data1$comment_classification[1], 'debt for ', data1$project_name[1]), ylab="Number of days")
summary(data1)

# calculating survival plots apache-ant
library(survival) 
library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
######################################################################################################################################################
# without taking into consideration different types of td
postgresql <- dbSendQuery(con, "select 'Ant' as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-ant' and b.comment_classification in ('DEFECT','DESIGN','TEST') order by 4")
######################################################################################################################################################
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
survival.objects = Surv(data1$epoch_interval/86400, data1$was_td_removed)
my.fit = survfit(survival.objects ~ data1$comment_classification)
plot (my.fit, main=paste("Kaplan-Meier estimate for ",data1$project_name[1]), xlab="Time in Days", ylab="Survival Function", col = 1:4) 
legend(100, 0.3, legend=c("Defect","Design","Test"), col = 1:4, lty = 1)
summary(my.fit)

# calculating survival plots
library(survival) 
library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
######################################################################################################################################################
# without taking into consideration different types of td
postgresql <- dbSendQuery(con, "select 'Jmeter' as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-jmeter' and b.comment_classification in ('DEFECT','DESIGN') order by 4")
######################################################################################################################################################
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
survival.objects = Surv(data1$epoch_interval/86400, data1$was_td_removed)
my.fit = survfit(survival.objects ~ data1$comment_classification)
plot (my.fit, main=paste("Kaplan-Meier estimate for ",data1$project_name[1]), xlab="Time in Days", ylab="Survival Function", col = 1:2) 
legend(100, 0.3, legend=c("Defect","Design"), col = 1:2, lty = 1)
summary(my.fit)


library(survival) 
library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, host='localhost', port='5432', dbname='comment_classification', user='evermal', password='')
######################################################################################################################################################
# without taking into consideration different types of td
postgresql <- dbSendQuery(con, "select 'Jruby' as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'jruby' and b.comment_classification in ('DEFECT','DESIGN', 'IMPLEMENTATION', 'TEST') order by 4")
######################################################################################################################################################
data1 <- fetch(postgresql, n=-1)
dim(data1)
dbHasCompleted(postgresql)
survival.objects = Surv(data1$epoch_interval/86400, data1$was_td_removed)
my.fit = survfit(survival.objects ~ data1$comment_classification)
plot (my.fit, main=paste("Kaplan-Meier estimate for ",data1$project_name[1]), xlab="Time in Days", ylab="Survival Function", col = 1:4) 
legend(100, 0.4, legend=c("Defect","Design", "Implementation", "Test"), col = 1:4, lty = 1)
summary(my.fit)


######################################################################################################################################################
# taking into consideration different types of td
# postgresql <- dbSendQuery(con, "select 'Ant'     as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-ant' and b.comment_classification = 'DESIGN'")
# postgresql <- dbSendQuery(con, "select 'Ant'     as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-ant' and b.comment_classification = 'DEFECT'")
# postgresql <- dbSendQuery(con, "select 'Ant'     as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-ant' and b.comment_classification = 'TEST'")
# postgresql <- dbSendQuery(con, "select 'Jmeter'  as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-jmeter' and b.comment_classification = 'DESIGN'")
# postgresql <- dbSendQuery(con, "select 'Jmeter'  as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-jmeter' and b.comment_classification = 'DEFECT'")
# postgresql <- dbSendQuery(con, "select 'Jruby'   as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'jruby' and b.comment_classification = 'DESIGN'")
# postgresql <- dbSendQuery(con, "select 'Jruby'   as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'jruby' and b.comment_classification = 'DEFECT'")
# postgresql <- dbSendQuery(con, "select 'Jruby'   as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'jruby' and b.comment_classification = 'TEST'")
# postgresql <- dbSendQuery(con, "select 'Jruby'   as project_name, a.was_td_removed, a.epoch_interval, b.comment_classification from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'jruby' and b.comment_classification = 'IMPLEMENTATION'")
######################################################################################################################################################

######################################################################################################################################################
# all projects and all types together
# postgresql <- dbSendQuery(con, "select was_td_removed, epoch_interval from survival_plot ")
######################################################################################################################################################

# ####################################################################################################################################################
# adding only the removed samples indicates that we expect that the population (td) will be dead (removed) at the end of the experiment
# postgresql <- dbSendQuery(con, "select was_td_removed, epoch_interval from survival_plot where project_name = 'apache-ant' and was_td_removed = 1")
# postgresql <- dbSendQuery(con, "select was_td_removed, epoch_interval from survival_plot where project_name = 'apache-jmeter' and was_td_removed = 1")
# postgresql <- dbSendQuery(con, "select was_td_removed, epoch_interval from survival_plot where project_name = 'jruby' and was_td_removed = 1")
######################################################################################################################################################

######################################################################################################################################################
# there are some types of td that are never removed
# postgresql <- dbSendQuery(con, "select a.was_td_removed, a.epoch_interval from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-ant' and b.comment_classification = 'IMPLEMENTATION'")
# postgresql <- dbSendQuery(con, "select a.was_td_removed, a.epoch_interval from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-jmeter' and b.comment_classification = 'TEST'")
# postgresql <- dbSendQuery(con, "select a.was_td_removed, a.epoch_interval from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-jmeter' and b.comment_classification = 'IMPLEMENTATION'")
# postgresql <- dbSendQuery(con, "select a.was_td_removed, a.epoch_interval from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'apache-jmeter' and b.comment_classification = 'DOCUMENTATION'")
# postgresql <- dbSendQuery(con, "select a.was_td_removed, a.epoch_interval from survival_plot a, time_to_remove_td b where a.processed_comment_id = b.processed_comment_id and a.project_name = 'jruby' and b.comment_classification = 'DOCUMENTATION'")
######################################################################################################################################################