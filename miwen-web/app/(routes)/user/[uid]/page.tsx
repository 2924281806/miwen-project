"use client";
import { useParams } from "next/navigation";
export default function User() {
  const { uid } = useParams();
  return (
    <div className="container">
      <h1>User{uid}</h1>
    </div>
  );
}
