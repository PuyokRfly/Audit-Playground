'use client';

import { useState } from 'react';
import Link from 'next/link';
import styles from './page.module.css';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [submissionId, setSubmissionId] = useState<string | null>(null);
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setIsLoading(true);
    setSubmissionId(null);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const uploadUrl = `${baseUrl}/upload/`;

    try {
      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }

      setSubmissionId(data.submission_id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>Smart Contract Auditor</h1>
        <p className={styles.description}>
          Upload a Solidity (.sol) file to check for vulnerabilities.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".sol"
            className={styles.input}
          />
          <button type="submit" className={styles.button} disabled={isLoading}>
            {isLoading ? 'Uploading...' : 'Upload and Analyze'}
          </button>
        </form>

        {submissionId && (
          <div className={styles.successMessage}>
            <p>File uploaded successfully!</p>
            <Link href={`/submission/${submissionId}`} className={styles.link}>
              View Audit Report
            </Link>
          </div>
        )}
        {error && <p className={styles.errorMessage}>{error}</p>}
      </div>
    </main>
  );
}
