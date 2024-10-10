"use client";

import { useEffect, useRef, useState } from "react";
import { gql, useMutation } from "@apollo/client";

// Define the GraphQL mutation
const GET_FOOD_FROM_IMAGE_MUTATION = gql`
  mutation GetFoodFromImage($foodImage: String!) {
    getFoodFromImage(foodImage: {base64Image: $foodImage}) {
      name
      plasticAmounts{
        plasticType
        amount
        unit
      }
    }
  }
`;

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [getFoodFromImage] = useMutation(GET_FOOD_FROM_IMAGE_MUTATION);
  const [foodData, setFoodData] = useState<any>(null);

  useEffect(() => {
    // Check if the browser supports getUserMedia
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      console.log("getUserMedia supported");
      // Request access to the camera
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
          // Set the video stream to the video element's source
          if (videoRef.current) {
            (videoRef.current as HTMLVideoElement).srcObject = stream;
          }
        })
        .catch((error) => {
          console.log("Something went wrong!", error);
        });
    } else {
      alert("getUserMedia not supported by this browser.");
    }
  }, []); // Empty dependency array ensures this runs once when the component mounts

  const captureAndSendImage = async () => {
    alert("captureAndSendImage");
    console.log("captureAndSendImage");
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d')?.drawImage(video, 0, 0);
      
      const base64Image = canvas.toDataURL('image/jpeg').split(',')[1];
      
      try {
        const result = await getFoodFromImage({ variables: { foodImage: base64Image } });
        console.log('Image sent successfully:', result);
        setFoodData(result.data.getFoodFromImage);
      } catch (error) {
        console.error('Error sending image:', error);
        setFoodData(null);
      }

      // Add this block to restart the video stream
      if (video.srcObject instanceof MediaStream) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
      
      try {
        const newStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = newStream;
        video.play();
      } catch (error) {
        console.error('Error restarting video stream:', error);
      }
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Food Analyzer</h1>
      {videoRef && (
        <>
          <video ref={videoRef} width="640" height="480" autoPlay playsInline className="mb-4" />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4" onClick={captureAndSendImage}>Analyze Food</button>
        </>
      )}
      {foodData && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <h2 className="text-xl font-semibold mb-2">Analysis Results</h2>
          <p className="mb-2"><strong>Food Name:</strong> {foodData.name}</p>
          <h3 className="text-lg font-semibold mb-2">Plastic Amounts:</h3>
          <ul className="list-disc pl-5">
            {foodData.plasticAmounts.map((plastic: any, index: number) => (
              <li key={index}>
                {plastic.plasticType}: {plastic.amount} {plastic.unit}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
