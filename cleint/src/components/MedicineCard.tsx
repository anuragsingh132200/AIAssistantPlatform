import React from "react";

interface MedicineCardProps {
  drug_name: string;
  available_in_region: boolean | null;
  prescription?: boolean;
  generic?: string;
  usage?: string;
  price?: string;
  reviews?: string;
  match?: string;
  side_effects?: string;
  onFindNearby?: () => void;
  onDetails?: () => void;
}

export default function MedicineCard({
  drug_name,
  available_in_region,
  prescription,
  generic,
  usage,
  price,
  reviews,
  match,
  side_effects,
  onFindNearby,
  onDetails
}: MedicineCardProps) {
  return (
    <div className="bg-white rounded-xl shadow p-5 mb-4 flex flex-col gap-2 border">
      <div className="flex items-center gap-2 mb-1">
        <span className="font-bold text-lg">{drug_name}</span>
        {available_in_region === true && <span className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full font-semibold">Available</span>}
        {available_in_region === false && <span className="bg-red-100 text-red-800 text-xs px-2 py-0.5 rounded-full font-semibold">Out of Stock</span>}
        {prescription && <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full font-semibold">Prescription</span>}
      </div>
      {generic && <div className="text-xs text-gray-700">Generic: {generic}</div>}
      {usage && <div className="text-xs text-gray-700">Commonly used for: {usage}</div>}
      <div className="flex items-center gap-4 text-xs mt-1">
        {price && <span className="font-semibold">${price}</span>}
        {reviews && <span>{reviews} reviews</span>}
        {match && <span>Match: {match}</span>}
      </div>
      {side_effects && <div className="text-xs text-gray-500 mt-1">Side effects: {side_effects}</div>}
      <div className="flex gap-2 mt-3">
        <button className="bg-blue-600 text-white px-4 py-1 rounded flex-1 hover:bg-blue-700 transition text-sm" onClick={onFindNearby}>Find Nearby</button>
        <button className="border border-blue-600 text-blue-600 px-4 py-1 rounded flex-1 hover:bg-blue-50 transition text-sm" onClick={onDetails}>Details</button>
      </div>
    </div>
  );
} 