const data = [
    {
        "ID": "1",
        "Timestamp": "2024-05-05 16:37:55",
        "Status": "True",
        "Temperature": "20.01",
        "Humidity": "55.74",
        "Lux Level": "13.36"
    },
    {
        "ID": "2",
        "Timestamp": "2024-05-05 16:37:55",
        "Status": "True",
        "Temperature": "20.01",
        "Humidity": "100.74",
        "Lux Level": "13.36"
    },
    {
        "ID": "2",
        "Timestamp": "2024-05-06 18:37:55",
        "Status": "True",
        "Temperature": "20.01",
        "Humidity": "100.74",
        "Lux Level": "13.36"
    },
    {
        "ID": "2",
        "Timestamp": "2024-05-05 19:37:55",
        "Status": "True",
        "Temperature": "20.01",
        "Humidity": "100.74",
        "Lux Level": "13.36"
    },
];

const totalDetectedCount = data.filter(item => item.Status === "True").length;

console.log(`Total Detected Count: ${totalDetectedCount}`);



const hourlyDetections = {};

data.forEach(item => {
    const hour = item.Timestamp.slice(0, 13); // Extract YYYY-MM-DD HH
    if (item.Status === "True") {
        hourlyDetections[hour] = (hourlyDetections[hour] || 0) + 1;
    }
});

const hours = Object.keys(hourlyDetections).map(hour => `${hour}:00`);
const detectionCounts = Object.values(hourlyDetections);



console.log("Hours:", hours);
console.log("Detection Counts:", detectionCounts);



const dailyDetections = {};

data.forEach(item => {
    const date = item.Timestamp.slice(0, 10); // Extract YYYY-MM-DD
    if (item.Status === "True") {
        dailyDetections[date] = (dailyDetections[date] || 0) + 1;
    }
});

const dates = Object.keys(dailyDetections);
const dailyDetectionCounts = Object.values(dailyDetections);






const detections = data.filter(item => item.Status === "True");



const temperatures = detections.map(item => parseFloat(item.Temperature));
const humidities = detections.map(item => parseFloat(item.Humidity));
const luxLevels = detections.map(item => parseFloat(item["Lux Level"]));



const timestamps = detections
    .map(item => new Date(item.Timestamp))
    .sort((a, b) => a - b);

const timeDifferences = [];

for (let i = 1; i < timestamps.length; i++) {
    const diff = timestamps[i] - timestamps[i - 1]; // Difference in milliseconds
    timeDifferences.push(diff);
}

const averageDiff = timeDifferences.reduce((a, b) => a + b, 0) / timeDifferences.length;
const avgTimeBetweenDetections = averageDiff / (1000 * 60); // Convert to minutes

const now = new Date();
const lastDetectionTime = timestamps[timestamps.length - 1];
const timeSinceLastDetection = now - lastDetectionTime;

const formatTimeAgo = (milliseconds) => {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const months = Math.floor(days / 30);
    const years = Math.floor(months / 12);

    if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`;
    if (months > 0) return `${months} month${months > 1 ? 's' : ''} ago`;
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return `${seconds} second${seconds > 1 ? 's' : ''} ago`;
};

const avgTimeBetweenDetectionsFormatted = formatTimeAgo(averageDiff);
const lastDetectionTimeFormatted = formatTimeAgo(timeSinceLastDetection);



const lastObj={
    totalDetectedCount:totalDetectedCount,
    hourlyDetections:{
        hours:hours,
        detectionCounts:detectionCounts,
    },
    dailyDetectionCount:{
        dates:dates,
        detectionCounts:dailyDetectionCounts,
    },
    env_conditions_during_detections:{
        temperatures:temperatures,
        humidities:humidities,
        luxLevels:luxLevels,
    },
    avgTimeBetweenDetections:avgTimeBetweenDetectionsFormatted,
    lastDetectionTime:lastDetectionTimeFormatted,
    
}


console.log("lastObj:", lastObj);
