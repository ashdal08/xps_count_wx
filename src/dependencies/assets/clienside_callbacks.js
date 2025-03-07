window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    plot_update_test: function (reset_plot, new_point, pass_no) {
      let graphDiv = document.querySelector(
        "#live-update-graph .js-plotly-plot"
      );
      if (reset_plot) {
        let traces = [];
        for (let i = 0; i < pass_no; i++) {
          Plotly.deleteTraces(graphDiv, i);
        }
        // Plotly.deleteTraces(graphDiv, traces);
        Plotly.addTraces(
          graphDiv,
          {
            x: [],
            y: [],
            name: "pass_1",
            mode: "markers+lines",
            line_width: 1,
            marker_size: 4,
          },
          pass_no - 1
        );
        return;
      }
      Plotly.extendTraces(
        graphDiv,
        { x: [[new_point[0]]], y: [[new_point[1]]] },
        [pass_no - 1]
      );
      var update = {
        mode: "markers+lines",
        "line.width": 1,
        "marker.size": 4,
        name: "pass_" + pass_no,
      };
      Plotly.restyle(graphDiv, update, pass_no - 1);
      return;
    },
    plot_update: function (n, data, layout) {
      return {
        data: data,
        layout: layout,
      };
    },
  },
});
