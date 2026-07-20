import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

/**
 * Catches render-time errors so a single broken component degrades into a
 * readable message instead of blanking the entire app. Class component by
 * necessity — hooks have no equivalent of componentDidCatch.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('Unhandled UI error:', error, info?.componentStack);
  }

  handleReset = () => {
    this.setState({ error: null });
  };

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md bg-card rounded-3xl p-6 sm:p-8 shadow-2xl border border-red-500/20 text-center space-y-5">
          <div className="mx-auto w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
            <AlertTriangle className="h-6 w-6 text-red-400" />
          </div>

          <div className="space-y-2">
            <h1 className="text-xl font-bold text-white">Something went wrong</h1>
            <p className="text-sm text-zinc-400 leading-relaxed">
              This section failed to render. You can retry, or head back to the dashboard.
            </p>
          </div>

          {import.meta.env.DEV && (
            <pre className="text-left text-[10px] text-red-300 bg-black/30 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap break-words">
              {this.state.error.message}
            </pre>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={this.handleReset}
              className="flex-1 flex items-center justify-center gap-2 py-3 btn-primary rounded-xl text-xs font-extrabold uppercase tracking-wider"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Try again
            </button>
            <a
              href="/"
              className="flex-1 flex items-center justify-center py-3 bg-surface border border-zinc-200 rounded-xl text-xs font-extrabold uppercase tracking-wider text-text"
            >
              Go home
            </a>
          </div>
        </div>
      </div>
    );
  }
}
