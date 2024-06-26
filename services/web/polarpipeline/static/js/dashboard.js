
document.addEventListener("DOMContentLoaded", function () {
    const editButton = document.getElementById("editButton");
    const deleteButtons = document.querySelectorAll(".delete-button");
    const infoButtons = document.querySelectorAll(".info-button");

    editButton.addEventListener("click", function () {
        deleteButtons.forEach(function (button) {
            button.style.display = editButton.classList.contains("active") ? "none" : "inline-block";
        });
        infoButtons.forEach(function (button) {
            button.style.display = editButton.classList.contains("active") ? "inline-block" : "none";
        });

        editButton.classList.toggle("active");
    });

    graphs();
});

function submitForm() {
    // Get the file input element
    var fileInput = document.getElementById('fileInput');
    
    // Check if a file is selected
    if (fileInput.files.length == 0) {
        alert('Please select a file.');
        return;
    }
    
    // Submit the form
    var formData = new FormData(document.getElementById('importForm'));
    fetch('/importProgress', {
        method: 'POST',
        body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.error) {
                console.error(data.error);
            } else {
                location.reload();
            }
        })
    .catch(error => console.error('Error:', error));
}

function handleDeleteClick(rowId) {
    const modalVal = document.getElementById("deleteItemModal");
    modalVal.value = rowId;
}

function deleteItem() {
    const modalVal = document.getElementById("deleteItemModal").value;
    window.location.href = "/deleteRun/" + modalVal
}

function graphs(){

    var labels = formattedData.map(row => row.computer);
    var data = formattedData.map(row => row.runtime);
    var ctx = document.getElementById('runtimeChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Runtime (hours)',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            legend: {
                position: 'top'
            },
            responsive: true,
        }
    });


    var refLabels = referenceData.map(row => row.reference);
    var refData = referenceData.map(row => row.count);
    var fullLabels = refLabels;
    var abbreviatedLabels = fullLabels.map(label => label.length > 5 ? label.slice(0, 15) + '...' : label);
    var dynamicColors = [];
    for (var i = 0; i < refLabels.length; i++) {
        var r = Math.floor(Math.random() * 256);
        var g = Math.floor(Math.random() * 256);
        var b = Math.floor(Math.random() * 256);
        var color = 'rgba(' + r + ',' + g + ',' + b + ', 0.6)';
        dynamicColors.push(color);
    }
    var refctx = document.getElementById('refChart').getContext('2d');
    var refChart = new Chart(refctx, {
        type: 'pie',
        data: {
            labels: abbreviatedLabels,
            datasets: [{
                label: 'Reference Counts',
                data: refData,
                backgroundColor: dynamicColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItem){
                            return fullLabels[tooltipItem[0].dataIndex];
                        }
                    }
                }
            }
        }
    });


    var computers = [...new Set(refTimingData.map(item => item.computer))];
    var references = [...new Set(refTimingData.map(item => item.reference))];
    var fullLabels = references;
    var abbreviatedLabels = fullLabels.map(label => label.length > 5 ? label.slice(0, 15) + '...' : label);


    var dynamicColors = {};
    computers.forEach((computer, index) => {
        var r = Math.floor(Math.random() * 256);
        var g = Math.floor(Math.random() * 256);
        var b = Math.floor(Math.random() * 256);
        dynamicColors[computer] = ['rgba(' + r + ',' + g + ',' + b + ',0.6)', 'rgba(' + r + ',' + g + ',' + b + ',1)'];
    });
    var datasets = [];
    computers.forEach(computer => {
        var dataset = {
            label: computer,
            backgroundColor: [],
            borderColor: [],
            borderWidth: 2,
            data: []
        };
        references.forEach(reference => {
            var runtime = refTimingData.find(item => item.reference === reference && item.computer === computer)?.runtime || null;
            dataset.backgroundColor.push(dynamicColors[computer][0]);
            dataset.borderColor.push(dynamicColors[computer][1])
            dataset.data.push(runtime);
        });
        datasets.push(dataset);
    });
    // console.log(datasets);
    var refTimingCtx = document.getElementById('refTimingChart').getContext('2d');
    var reftimchart = new Chart(refTimingCtx, {
        type: 'bar',
        data: {
            labels: abbreviatedLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItem){
                            return fullLabels[tooltipItem[0].dataIndex];
                        }
                    }
                }
            }
        }
    });



}


function updateStatus(){
    var idlist = [];
    document.querySelectorAll('.status').forEach(element => {
        idlist.push(element.getAttribute('data-value'));
    });
    // console.log(idlist);

    fetch('/update-dashboard', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ job_ids: idlist })
    })
    .then(response => response.json())
    .then(data => {
        // console.log('Success:', data);

        const statusCard = document.getElementById('statusCard');
        statusCard.innerHTML = ''; // Clear existing content

        if (data.nodes && data.nodes.length > 0) {
            data.nodes.forEach(node => {
                // Create the row div
                const rowDiv = document.createElement('div');
                rowDiv.className = 'row align-items-center';

                // Create the image div
                const imgDiv = document.createElement('div');
                imgDiv.className = 'col-auto';
                const img = document.createElement('img');
                img.src = '/static/server.png'; // Ensure this path is correct
                img.className = 'icon';
                img.style.width = '30px';
                img.style.height = '30px';
                imgDiv.appendChild(img);

                // Create the text div
                const textDiv = document.createElement('div');
                textDiv.className = 'col-auto';
                const span = document.createElement('span');
                span.innerText = node;
                textDiv.appendChild(span);

                // Append image and text divs to the row div
                rowDiv.appendChild(imgDiv);
                rowDiv.appendChild(textDiv);

                // Append the row div to the statusCard
                statusCard.appendChild(rowDiv);
            });
        } else {
            console.log('No nodes data returned.');
        }

        Object.entries(data.jobs).forEach(([jobId, status]) => {
            // console.log(`Job ID: ${jobId}, Status: ${status}`);
            $('#'+jobId).text(status)
        });

    })
    .catch((error) => {
        console.error('Error:', error);
    });
    setTimeout(updateStatus, 1000);
}
updateStatus();