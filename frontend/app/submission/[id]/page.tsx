'use client';

import { useEffect, useState } from 'react';
import styles from './submission.module.css';

// Mock Slither data for demonstration purposes
const MOCK_REPORT = {
  "success": true,
  "error": null,
  "results": {
    "detectors": [
      {
        "elements": [
          { "type": "function", "name": "withdraw" }
        ],
        "description": "Reentrancy in Vulnerable.withdraw(uint256)",
        "markdown": "Reentrancy in `Vulnerable.withdraw(uint256)`",
        "check": "reentrancy-eth",
        "impact": "High",
        "confidence": "Medium"
      },
      {
        "elements": [
          { "type": "pragma", "name": "^0.8.0" }
        ],
        "description": "Version constraint ^0.8.0 contains known severe issues.",
        "markdown": "Version constraint `^0.8.0` contains known severe issues.",
        "check": "solc-version",
        "impact": "Informational",
        "confidence": "High"
      },
      {
        "elements": [
            { "type": "function", "name": "send" }
        ],
        "description": "Use of deprecated `send` function.",
        "markdown": "Use of deprecated `send` function.",
        "check": "low-level-calls",
        "impact": "Low",
        "confidence": "High"
      }
    ]
  }
};

type Detector = {
  check: string;
  impact: string;
  confidence: string;
  description: string;
};

export default function SubmissionPage({ params }: { params: { id: string } }) {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real application, you would fetch the report from your backend
    // using the submission ID from `params.id`.
    // For now, we'll simulate a network request and use mock data.
    const fetchReport = async () => {
      setLoading(true);
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        // This is where you'd fetch(`.../api/submission/${params.id}`)
        if (params.id) {
          setReport(MOCK_REPORT.results);
        } else {
          throw new Error("Submission ID not found.");
        }

      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [params.id]);

  const getImpactClass = (impact: string) => {
    switch (impact) {
      case 'High': return styles.high;
      case 'Medium': return styles.medium;
      case 'Low': return styles.low;
      default: return styles.informational;
    }
  };

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>Audit Report</h1>
        <p className={styles.subheading}>Submission ID: {params.id}</p>

        {loading && <p>Loading report...</p>}
        {error && <p className={styles.errorMessage}>Error: {error}</p>}

        {report && (
          <div className={styles.reportContainer}>
            <h2 className={styles.findingsTitle}>
              {report.detectors.length} findings
            </h2>
            {report.detectors.map((detector: Detector, index: number) => (
              <div key={index} className={styles.detectorCard}>
                <h3 className={styles.detectorCheck}>{detector.check}</h3>
                <p className={styles.detectorDescription}>{detector.description}</p>
                <div className={styles.detectorMeta}>
                  <span className={`${styles.badge} ${getImpactClass(detector.impact)}`}>
                    {detector.impact}
                  </span>
                  <span className={`${styles.badge} ${styles.confidence}`}>
                    {detector.confidence} Confidence
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
