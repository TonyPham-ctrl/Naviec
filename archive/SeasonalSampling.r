filepath <- paste('data/','partial_single_day.csv',sep="")

dat <- read.csv(filepath, sep=',', header=TRUE, dec='.', stringsAsFactors=TRUE)

# Getting the population mean, that is, the mean of the RRP within a year.
theta <- mean(dat$RRP)

# Initialise the stratum for each season, as seasonal change impact a lot on power usage
# The vector contains the months
spring <- c('09','10','11')
summer <- c('12','01','02')
autumn <- c('03','04','05')
winter <- c('06','07','08')

# Remove the time in the date. Since I will use mean of date to try to estimate the population mean later.
dat <- transform(dat, date=as.Date(SETTLEMENTDATE))
dat$SETTLEMENTDATE <- NULL

# Calculating the mean of each day
daily_means <- aggregate(RRP ~ date, data=dat, FUN=mean)

# Split daily_means into groups of means by month.
means_by_month <- split(daily_means, format(daily_means$date, "%m"))
head(means_by_month)

means_by_month[spring]
#======== Stratified Sampling on the year, by having strata of months ===========
N <- 12
n <- 4
m <- 3

# Total samples should be 81. 
all_samples <- t(unname(expand.grid(spring, summer, autumn, winter)))

# Calculating the sample means (yes, means of all the sample)
# unlist(sapply(means_by_month[spring], function(l) l[2]), use.names=FALSE)
sample_means <- apply(all_samples, MARGIN=2, function(sample){
    sample_data <- unlist(sapply(means_by_month[sample], function(l) l[2]), use.names=FALSE)
    sum(sample_data)/length(sample_data)
})

hist(sample_means)

bias <- mean(sample_means) - theta
SE <- sqrt(mean((sample_means - mean(sample_means))**2))
MSE <- bias**2 + SE**2
print(bias)
print(SE)
print(MSE)