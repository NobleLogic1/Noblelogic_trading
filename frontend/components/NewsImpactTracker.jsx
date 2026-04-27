import React, { useEffect, useState } from 'react';

export default function NewsImpactTracker() {
  const [news, setNews] = useState([]);

  useEffect(() => {
    fetch('https://cryptopanic.com/api/posts/?auth_token=demo&public=true')
      .then(res => res.json())
      .then(data => setNews(data.results.slice(0, 5)));
  }, []);

  return (
    <div className="panel">
      <h2>📣 News Impact Tracker</h2>
      <ul>
        {news.map((n, i) => (
          <li key={i}>
            <a href={n.url} target="_blank" rel="noreferrer">{n.title}</a>
            <br />
            <small>{n.published_at}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}