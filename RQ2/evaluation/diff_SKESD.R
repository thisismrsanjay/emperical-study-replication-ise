
library(ScottKnottESD)


# Create legend vector.
make_legend <- function(sk,dat){
    v = as.vector(NULL)
    for(nms in dat$variable){
        if(nms=='TCA+'){
            temp = sk$groups['TCA.']
        }
        else{
            temp = sk$groups[nms]
        }
        v = c(v,temp)
    }
    return(v)
}


create_boxplot <- function(dat,plot_name,xlabel,ylabel) {
    sk <- sk_esd(dat)

    dat = melt(dat)
    dat$variable <- with(dat, reorder(variable,value,mean))

    V2 = make_legend(sk,dat)

    dat <- transform(dat,V2=V2)


    g <- ggplot(
        dat,
        aes(
            x = variable,
            y = value,
            fill=factor(V2)
        )
    )

    g <- g + geom_boxplot(aes(linetype=factor(V2)))
    g <- g + ylab(ylabel)
    g <- g + xlab(xlabel)
    #g <- g + coord_cartesian(ylim=c(0.0,0.3))
    #g <- g + theme(axis.text.x = element_text(angle = 45, hjust = 1, size=20), axis.text.y = element_text(size=20))
    #g <- g + theme(axis.title.y = element_text(size=20))
    g <- g + theme(axis.text.x = element_text(angle = 45, hjust = 1, size=10), axis.text.y = element_text(size=10))
    g <- g + theme(axis.title.y = element_text(size=10))
    g <- g + theme(legend.position="none")
    g <- g + theme(panel.grid.major=element_blank(), panel.grid.minor=element_blank(), panel.background=element_blank())
    g <- g + theme(axis.line.x = element_line(color="black", size = 0.5),axis.line.y = element_line(color="black", size = 0.5))

    pdf(plot_name, width=7, height=3.5)

    plot(g)

    return(sk)
}


