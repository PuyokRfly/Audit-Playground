'use client';

import { useState, FormEvent } from 'react';
import { supabase } from '../../lib/supabase';

export default function Dashboard() {
  const [code, setCode] = useState('');
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Fetch user on component mount
  useState(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
    };
    getUser();
  });

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage('');

    if (!user) {
      setMessage('You must be logged in to submit code for audit.');
      setLoading(false);
      return;
    }

    if (!code.trim()) {
      setMessage('Please enter some Solidity code.');
      setLoading(false);
      return;
    }

    // NOTE: Replace with your actual n8n webhook URL
    const webhookUrl = 'https://n8n.example.com/webhook/your-webhook-id';

    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          user_id: user.id,
        }),
      });

      if (response.ok) {
        setMessage('Code submitted successfully for audit!');
        setCode('');
      } else {
        const errorData = await response.json();
        setMessage(`Error: ${errorData.message || 'Something went wrong.'}`);
      }
    } catch (error) {
      setMessage('Error: Could not connect to the audit service.');
      console.error('Submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-4">Smart Contract Audit</h1>
      <p className="mb-4">
        {user ? `Welcome, ${user.email}` : 'Please sign in to use the service.'}
      </p>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="solidity-code" className="block text-sm font-medium text-gray-700">
            Solidity Code
          </label>
          <textarea
            id="solidity-code"
            name="solidity-code"
            rows={15}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-black"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Enter your Solidity code here..."
          />
        </div>
        <div>
          <button
            type="submit"
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit for Audit'}
          </button>
        </div>
      </form>
      {message && <p className="mt-4 text-sm text-gray-600">{message}</p>}
    </div>
  );
}
