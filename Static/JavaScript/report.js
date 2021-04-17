const ctx = document.getElementById("myChart").getContext("2d");
const ctx2 = document.getElementById("myChart1").getContext("2d");
const ctx3 = document.getElementById("myChart2").getContext("2d");

const config = {
    type: "line",
    data: {
      labels: ["1:00 PM","1:30 PM","2:00 PM","2:30 PM","3:00 PM","3:30 PM"],
      datasets: [
        {
          label: "Count",
          data: [12, 19, 3, 5, 2, 3],
          borderColor: [
            "rgba(41, 217, 179, 1)",
              ],
           backgroundColor: 'rgba(41, 217, 179, 0.8)',
              borderWidth: 3,
              tension: 0.1
        },
      ],
    },
  options: {
            animation : false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: "rgba(0,0,0, 0.9)",
                        font: 20,
                        padding : 20
                    }
              },
                x : {
                    beginAtZero: false,
                    ticks: {
                        color: "rgba(0,0,0, 0.9)",
                        font: 20,
                        padding : 20
                    }
              }
                    },
            layout:{
            padding: 20,
          },
             plugins: {
            legend: {
                labels: {
                    // This more specific font property overrides the global property
                    font: {
                        size: 14
                    }
                    ,
                    color : "rgba(0,0,0,1)"
                }
            }
        }
    },
  }


const myChart = new Chart(ctx, {
 ...config,
  data: {
    ...config.data,
    datasets:  [
        {
          label: "Count",
          data: [7,6,10,5,9,10],
          borderColor: [
            "rgba(41, 217, 179, 1)",
              ],
           backgroundColor: 'rgba(41, 217, 179, 0.8)',
              borderWidth: 3,
              tension: 0.1
        },
      ],
  }
});



const myChart2 = new Chart(ctx2, {
  ...config,
  data: {
    ...config.data,
    datasets:  [
        {
          label: "Count",
          data: [5,3,1,4,8,6],
          borderColor: [
            "rgba(41, 217, 179, 1)",
              ],
           backgroundColor: 'rgba(41, 217, 179, 0.8)',
              borderWidth: 3,
              tension: 0.1
        },
      ],
  }
});



const myChart3 = new Chart(ctx3, {
  ...config,
  data: {
    ...config.data,
    datasets:  [
        {
          label: "Count",
          data:  [12,9,11,9,17,16],
          borderColor: [
            "rgba(41, 217, 179, 1)",
              ],
           backgroundColor: 'rgba(41, 217, 179, 0.8)',
              borderWidth: 3,
              tension: 0.1
        },
      ],
  }
  
})


  













const list = JSON.parse(`{{allCameras | tojson | safe}}`);
const length = list.length;

const matrix = [];
const max_size = 8;
const timeArray = []
let time = new Date(new Date().getTime() + 60 * 1000)
    .toTimeString()
    .toString()
    .slice(0, 8);

list.forEach((element, index) => {
  const xhr = new XMLHttpRequest();
  const id = String(element._id);
  const url = `/count_stream/${id}`;
  let max = 0;

  xhr.open("GET", url);
  xhr.send();

  const canvas = document.getElementById(id).getContext("2d");

 

  const display = () => {
  const currTime = new Date().toTimeString().toString().slice(0, 8);
  const message = xhr.responseText;
  const l = message.split("*");

  if (max < +l[l.length - 1]) {
    max = +l[l.length - 1];
  }

  if (time == currTime) {
    matrix[index] = matrix[index].push({ currTime: max });
    timeArray.push()
    if (matrix[index].length === max_size) {
      matrix[index].shift();
    }
  }    
  };



  const myChart = new Chart(canvas, {
 ...config,
  data: {
    ...config.data,
    labels: matrix[index].map(ele => {
      for (let value in ele) {
        return value;
      }
    } ),
    datasets:  [
        {
          label: "Count",
          data:  matrix[index].map(ele => {
      for (let value in ele) {
        return ele[value];
      }
    } ),
          borderColor: [
            "rgba(41, 217, 179, 1)",
              ],
           backgroundColor: 'rgba(41, 217, 179, 0.8)',
              borderWidth: 3,
              tension: 0.1
        },
      ],
  }
});



  setInterval(display, 100);
  });