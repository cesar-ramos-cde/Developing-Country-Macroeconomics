library(ggplot2)

df <- data.frame(
  indicator = c("Participation rate", "Inactivity rate",
                "Employment rate", "Unemployment rate*"),
  rate  = c(68.99, 31.01, 66.02, 4.30),
  lower = c(68.10, 30.12, 65.13, 3.86),
  upper = c(69.88, 31.90, 66.92, 4.75)
)
df$indicator <- factor(df$indicator, levels = rev(df$indicator))
df$label <- sprintf("%.1f%%  [%.1f, %.1f]", df$rate, df$lower, df$upper)

g <- ggplot(df, aes(x = rate, y = indicator)) +
  geom_segment(aes(x = 0, xend = rate, yend = indicator), color = "grey85", linewidth = 1) +
  geom_point(size = 3) +
  geom_text(aes(label = label), hjust = 0, nudge_x = 2, size = 3.5) +
  scale_x_continuous(limits = c(0, 100), expand = c(0, 0)) +
  labs(x = NULL, y = NULL,
       caption = paste0("* Share of labor force; other rates as share of working-age population.\n",
                        "95% confidence intervals in brackets. Source: INE, Encuesta de Hogares 2025.")) +
  theme_void(base_size = 12) +
  theme(axis.text.y  = element_text(hjust = 1, margin = margin(r = 8)),
        plot.caption = element_text(hjust = 0, color = "grey40", size = 9),
        plot.margin  = margin(10, 10, 10, 10))

ggsave("labor_rates_min.pdf", g, width = 6.5, height = 3)
ggsave("labor_rates_min.png", g, width = 6.5, height = 3, dpi = 300)