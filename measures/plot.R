library(ggplot2)
data <- read.csv(file="./perf_premier.csv", header=TRUE, sep=",")
seq = data[1, 'times']
# plot acceleration
data$acceleration = with(data, seq/times)
d = data.frame(cores=data$cores, acc=data$acceleration)
p = ggplot(d, aes(y=acc,x=cores)) + geom_line()
p <- p + labs(x="Nombre de coeur", y="Accéleration", title="Accéleration pour premier (cluster parapluie - 12 cpu avec 2 coeurs/cpu)")
p <- p + scale_x_continuous(breaks=pretty(data$cores, 10))
p <- p + scale_y_continuous(breaks=pretty(data$acceleration, 10))
p
ggsave("./acceleration_premier.svg", width = 2 * par("din")[1])
# plot efficacity

data$efficacity = with(data, acceleration/cores)
d = data.frame(cores=data$cores, eff=data$efficacity)
p = ggplot(d, aes(y=eff,x=cores)) + geom_line()
p <- p + labs(x="Nombre de coeur", y="Efficacité", title="Efficacité pour premier (cluster parapluie - 12 cpu avec 2 coeurs/cpu)")
p <- p + scale_x_continuous(breaks=pretty(data$cores, 10))
p <- p + scale_y_continuous(breaks=pretty(data$acceleration, 10))
p
ggsave("./efficacity_premier.svg", width = 2 * par("din")[1])
