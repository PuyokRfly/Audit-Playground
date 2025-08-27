'use client';

import { useState, useEffect } from 'react';
import { supabase } from '../../lib/supabase';

interface AuditResult {
  id: string;
  created_at: string;
  report: any; // Can be more specific based on the actual report structure
  contract_name: string;
}

export default function Results() {
  const [results, setResults] = useState<AuditResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const fetchUserAndResults = async () => {
      setLoading(true);
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);

      if (user) {
        try {
          const { data, error } = await supabase
            .from('audit_results')
            .select('*')
            .eq('user_id', user.id)
            .order('created_at', { ascending: false });

          if (error) {
            throw error;
          }

          setResults(data || []);
        } catch (err: any) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    fetchUserAndResults();
  }, []);

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-4">Audit Results</h1>

      {loading && <p>Loading...</p>}

      {!user && !loading && <p>Please log in to view your audit results.</p>}

      {error && <p className="text-red-500">Error: {error}</p>}

      {user && !loading && !error && (
        <>
          {results.length === 0 ? (
            <p>No audit results found.</p>
          ) : (
            <ul className="space-y-4">
              {results.map((result) => (
                <li key={result.id} className="p-4 border rounded-md shadow-sm">
                  <h2 className="text-xl font-semibold">{result.contract_name || 'Unnamed Contract'}</h2>
                  <p className="text-sm text-gray-500">
                    Audit Date: {new Date(result.created_at).toLocaleString()}
                  </p>
                  <div className="mt-2 p-2 bg-gray-50 rounded">
                    <h3 className="font-semibold">Report:</h3>
                    <pre className="whitespace-pre-wrap text-sm text-black">
                      {JSON.stringify(result.report, null, 2)}
                    </pre>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
