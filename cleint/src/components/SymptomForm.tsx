import React from "react";

interface Region {
  region_code: string;
  region_name: string;
}

interface SymptomFormProps {
  symptom: string;
  allergy: string;
  region: string;
  regions: Region[];
  onChange: (field: string, value: string) => void;
  onAutoDetect: () => void;
  onSubmit: (e: React.FormEvent) => void;
  autoDetecting: boolean;
}

export default function SymptomForm({
  symptom,
  allergy,
  region,
  regions,
  onChange,
  onAutoDetect,
  onSubmit,
  autoDetecting
}: SymptomFormProps) {
  return (
    <form className="bg-white rounded-xl shadow p-6 flex flex-col gap-4 min-w-[340px]" onSubmit={onSubmit}>
      <h2 className="text-xl font-bold flex items-center gap-2 mb-2">
        <span role="img" aria-label="stethoscope">🩺</span> Symptom Analysis
      </h2>
      <label className="block text-sm font-medium">Describe your symptoms <span className="text-red-500">*</span>
        <textarea
          className="w-full border p-2 rounded mt-1 resize-none min-h-[70px]"
          value={symptom}
          onChange={e => onChange("symptom", e.target.value)}
          required
          placeholder="e.g. fever and headache"
        />
      </label>
      <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
        Be as specific as possible for better recommendations
        <button type="button" className="ml-auto p-1" title="Auto-detect location" onClick={onAutoDetect} disabled={autoDetecting}>
          <span role="img" aria-label="location">📍</span>
        </button>
      </div>
      <label className="block text-sm font-medium">Known allergies (optional)
        <input
          className="w-full border p-2 rounded mt-1"
          value={allergy}
          onChange={e => onChange("allergy", e.target.value)}
          placeholder="e.g. penicillin"
        />
      </label>
      <label className="block text-sm font-medium">Your region <span className="text-red-500">*</span>
        <select
          className="w-full border p-2 rounded mt-1"
          value={region}
          onChange={e => onChange("region", e.target.value)}
          required
        >
          <option value="">Select region</option>
          {regions.map(r => (
            <option key={r.region_code} value={r.region_code}>{r.region_name}</option>
          ))}
        </select>
      </label>
      <button
        className="mt-4 bg-blue-600 text-white px-4 py-2 rounded font-semibold flex items-center justify-center gap-2 hover:bg-blue-700 transition"
        type="submit"
        disabled={autoDetecting}
      >
        <span role="img" aria-label="analyze">🧠</span> {autoDetecting ? "Detecting..." : "Analyze Symptoms"}
      </button>
    </form>
  );
} 