// export const processData = async (file, analyses, thresholds) => {
//   const formData = new FormData();
//   formData.append("file", file);
//   analyses.forEach((analysis) => formData.append("selections", analysis));
//   formData.append("acpsp_threshold", thresholds.ACPSP || 4);
//   formData.append("attenuation_threshold", thresholds.Attenuation || 2);
//   formData.append("cpcips_threshold", thresholds.CPCIPS || -1);

//   try {
//     const res = await fetch("http://localhost:8000/process-data/", {
//       method: "POST",
//       body: formData,
//       mode: "cors",
//       credentials: "include",
//     });

//     if (!res.ok) {
//       throw new Error(`HTTP error! status: ${res.status}`);
//     }

//     return await res.blob();
//   } catch (error) {
//     console.error("Fetch error:", error);
//     throw error;
//   }
// };

// export const processData = async (file, selections, thresholds) => {
//   const formData = new FormData();
//   formData.append("file", file);
//   selections.forEach(sel => formData.append("selections", sel));
//   formData.append("acpsp_threshold", thresholds.acpsp || 4);
//   formData.append("attenuation_threshold", thresholds.attenuation || 2);
//   formData.append("cpcips_threshold", thresholds.cpcips || -1.0);

//   const response = await fetch("http://localhost:8000/upload-and-process/", {
//     method: "POST",
//     body: formData,
//   });

//   if (!response.ok) {
//     const err = await response.json();
//     throw new Error(err.detail || "Something went wrong");
//   }

//   return await response.blob();
// };




// api.js

// Map frontend selection labels to backend processor keys
export const processorMap = {
  "Land Use": "land_use",
  "CIPS on PSP": "cips_on_psp",
  "Attenuation (ACCA)": "attenuation_acca",
  "AC PSP": "ac_psp",
  "AC Interference": "ac_interference",
};

// Function to process file with backend API
export const processData = async (file, selections, thresholds) => {
  const formData = new FormData();
  formData.append("file", file);

  // add thresholds
  formData.append("acpsp_threshold", thresholds.acpsp || 4);
  formData.append("attenuation_threshold", thresholds.attenuation || 2);
  formData.append("cpcips_threshold", thresholds.cpcips || -1.0);

  // loop through selected processors
  for (const sel of selections) {
    const key = processorMap[sel];
    if (!key) {
      console.warn(`⚠️ Unknown processor: ${sel}`);
      continue;
    }

    const response = await fetch(`http://127.0.0.1:8000/api/process/${key}/`, {
      method: "POST",
      body: formData,
    });

    // ✅ Better error handling
    if (!response.ok) {
      let errMsg = "Something went wrong";
      try {
        const err = await response.json();
        errMsg = err.error || err.detail || errMsg;
      } catch {
        errMsg = response.statusText || errMsg;
      }
      throw new Error(errMsg);
    }

    // return the processed Excel file
    return await response.blob();
  }
};
