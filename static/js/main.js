// Main script for general UI helpers and chart responsiveness
document.addEventListener("DOMContentLoaded", () => {
  // Auto-resize Plotly charts on window resize
  window.addEventListener("resize", () => {
    const plotContainers = document.querySelectorAll(".plotly-graph-div");
    plotContainers.forEach(div => {
      if (window.Plotly) {
        Plotly.Plots.resize(div);
      }
    });
  });
});
