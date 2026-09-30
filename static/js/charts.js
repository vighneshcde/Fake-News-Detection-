/**
 * Charts and Visualizations Controller
 * Handles Animated SVG Truth Gauge and Chart.js Radar & Breakdown Charts.
 */

window.AppCharts = (function () {
  let radarChartInstance = null;
  let breakdownChartInstance = null;

  // Initialize or update the SVG Truth Gauge
  function updateTruthGauge(score) {
    const scoreNum = document.getElementById("gauge-score-val");
    const fillArc = document.getElementById("gauge-fill-arc");
    const needle = document.getElementById("gauge-needle");

    if (!scoreNum || !fillArc) return;

    // Circumference of semi-circle arc (radius 85: arc length = pi * 85 ~= 267)
    const arcLength = 267;
    const clampedScore = Math.max(0, Math.min(100, score));
    const offset = arcLength - (arcLength * clampedScore) / 100;

    // Color gradient based on truth score
    let strokeColor = "#ef4444"; // Fake / Red
    let glowColor = "rgba(239, 68, 68, 0.4)";

    if (clampedScore >= 75) {
      strokeColor = "#10b981"; // Real / Green
      glowColor = "rgba(16, 185, 129, 0.4)";
    } else if (clampedScore >= 58) {
      strokeColor = "#38bdf8"; // Likely Real / Blue
      glowColor = "rgba(56, 189, 248, 0.4)";
    } else if (clampedScore >= 40) {
      strokeColor = "#f59e0b"; // Warning / Amber
      glowColor = "rgba(245, 158, 11, 0.4)";
    }

    fillArc.style.stroke = strokeColor;
    fillArc.style.strokeDashoffset = offset;
    fillArc.style.filter = `drop-shadow(0 0 8px ${glowColor})`;

    // Rotate needle from -90deg (0%) to +90deg (100%)
    if (needle) {
      const angle = -90 + (clampedScore / 100) * 180;
      needle.setAttribute("transform", `rotate(${angle} 120 120)`);
    }

    // Number roll-up animation
    animateScoreCounter(scoreNum, clampedScore);
  }

  function animateScoreCounter(elem, target) {
    let current = 0;
    const duration = 1000;
    const start = performance.now();

    function update(timestamp) {
      const elapsed = timestamp - start;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      current = eased * target;
      elem.textContent = current.toFixed(1) + "%";

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        elem.textContent = target.toFixed(1) + "%";
      }
    }
    requestAnimationFrame(update);
  }

  // Initialize or update Radar Chart
  function updateRadarChart(radarData) {
    const ctx = document.getElementById("radarChart");
    if (!ctx) return;

    const labels = [
      "Factual Rigor",
      "Emotional Neutrality",
      "Syntactic Quality",
      "Source Transparency",
      "Lexical Richness",
      "Domain Reputation"
    ];

    const values = [
      radarData.factual_rigor || 50,
      radarData.emotional_neutrality || 50,
      radarData.syntactic_quality || 50,
      radarData.source_transparency || 50,
      radarData.lexical_richness || 50,
      radarData.domain_reputation || 50
    ];

    if (radarChartInstance) {
      radarChartInstance.data.datasets[0].data = values;
      radarChartInstance.update();
      return;
    }

    radarChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Credibility Dimension",
            data: values,
            backgroundColor: "rgba(56, 189, 248, 0.2)",
            borderColor: "#38bdf8",
            borderWidth: 2,
            pointBackgroundColor: "#06b6d4",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "#06b6d4"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: "rgba(255, 255, 255, 0.08)" },
            grid: { color: "rgba(255, 255, 255, 0.08)" },
            pointLabels: {
              color: "#94a3b8",
              font: { family: "Inter", size: 11, weight: "600" }
            },
            ticks: {
              display: false,
              min: 0,
              max: 100,
              stepSize: 20
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "rgba(13, 21, 39, 0.9)",
            borderColor: "rgba(56, 189, 248, 0.4)",
            borderWidth: 1,
            bodyFont: { family: "Inter" }
          }
        }
      }
    });
  }

  // Initialize or update Model Consensus Breakdown
  function updateBreakdownChart(realProb, fakeProb) {
    const ctx = document.getElementById("breakdownChart");
    if (!ctx) return;

    if (breakdownChartInstance) {
      breakdownChartInstance.data.datasets[0].data = [realProb, fakeProb];
      breakdownChartInstance.update();
      return;
    }

    breakdownChartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Credible / Real", "Deceptive / Fake"],
        datasets: [
          {
            data: [realProb, fakeProb],
            backgroundColor: ["#10b981", "#ef4444"],
            borderColor: ["#059669", "#dc2626"],
            borderWidth: 1,
            hoverOffset: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "72%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: "#94a3b8",
              font: { family: "Inter", size: 11 }
            }
          }
        }
      }
    });
  }

  return {
    updateTruthGauge,
    updateRadarChart,
    updateBreakdownChart
  };
})();
