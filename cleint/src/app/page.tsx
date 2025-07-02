"use client";
import React, { useState } from "react";
import SymptomForm from "../components/SymptomForm";
import MedicineCard from "../components/MedicineCard";

const API_BASE = "http://localhost:8000";

export default function HomePage() {
  const [symptom, setSymptom] = useState("");
  const [allergy, setAllergy] = useState("");
  const [region, setRegion] = useState("");
  const [regions, setRegions] = useState<{ region_code: string; region_name: string }[]>([]);
  const [autoDetecting, setAutoDetecting] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  React.useEffect(() => {
    fetch(`${API_BASE}/regions`).then(r => r.json()).then(setRegions);
  }, []);

  const handleChange = (field: string, value: string) => {
    if (field === "symptom") setSymptom(value);
    if (field === "allergy") setAllergy(value);
    if (field === "region") setRegion(value);
  };

  const handleAutoDetect = () => {
    setAutoDetecting(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async () => {
        if (regions.length > 0) {
          setRegion(regions[Math.floor(Math.random() * regions.length)].region_code);
        }
        setAutoDetecting(false);
      }, () => setAutoDetecting(false));
    } else {
      setAutoDetecting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const params = new URLSearchParams({
      symptom,
      allergy,
      region,
      top_k: "10",
      min_confidence: "0.3"
    });
    const res = await fetch(`${API_BASE}/medicines?${params}`);
    const json = await res.json();
    setResults(json);
    setLoading(false);
  };

  // Mock price, reviews, prescription, and usage for demo
  const enrich = (med: any, i: number) => ({
    ...med,
    price: (20 + i * 4.5).toFixed(2),
    reviews: 100 + i * 17,
    prescription: true,
    generic: med.drug_name ? `Generic: ${med.drug_name}` : undefined,
    usage: med.medical_condition,
    match: med.confidence_score ? `${Math.round(med.confidence_score * 100)}%` : undefined
  });

  const filteredResults = results.filter(med =>
    (!search || med.drug_name.toLowerCase().includes(search.toLowerCase())) &&
    (!category || (category === "available" ? med.available_in_region : !med.available_in_region))
  );

  return (
    <main className="min-h-screen bg-gray-50 text-black">
      <header className="w-full py-4 px-8 bg-white shadow flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🧪</span>
          <span className="font-bold text-lg">MediFind AI</span>
        </div>
        <span className="text-xs text-gray-500">Smart Medicine Recommendations</span>
      </header>
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-8 mt-8 px-4">
        {/* Left panel: Symptom Analysis */}
        <div className="flex-1 max-w-md">
          <SymptomForm
            symptom={symptom}
            allergy={allergy}
            region={region}
            regions={regions}
            onChange={handleChange}
            onAutoDetect={handleAutoDetect}
            onSubmit={handleSubmit}
            autoDetecting={autoDetecting}
          />
        </div>
        {/* Right panel: Medicine Recommendations */}
        <div className="flex-[2] min-w-0">
          <div className="bg-white rounded-xl shadow p-6 mb-4">
            <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
              <span role="img" aria-label="pill">💊</span> Medicine Recommendations
            </h2>
            <div className="flex flex-col md:flex-row gap-2 mb-4">
              <input
                className="border p-2 rounded flex-1"
                placeholder="Search medicines..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
              <select
                className="border p-2 rounded w-48"
                value={category}
                onChange={e => setCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                <option value="available">Available</option>
                <option value="out">Out of Stock</option>
              </select>
            </div>
            {loading ? (
              <div className="text-center py-10">Analyzing symptoms...</div>
            ) : (
              <>
                {filteredResults.length === 0 && <div className="text-gray-500 text-center py-8">No medicine recommendations yet.</div>}
                {filteredResults.map((med, i) => (
                  <MedicineCard key={i} {...enrich(med, i)} />
                ))}
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
