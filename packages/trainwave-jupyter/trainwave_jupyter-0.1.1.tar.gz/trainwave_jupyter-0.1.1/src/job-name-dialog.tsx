import React from 'react';
import { Dialog } from '@jupyterlab/apputils';

export interface JobNameDialogProps {
  defaultName: string;
  onConfirm: (jobName: string) => void;
  onCancel: () => void;
}

export class JobNameDialog extends React.Component<
  JobNameDialogProps,
  { jobName: string }
> {
  constructor(props: JobNameDialogProps) {
    super(props);
    this.state = {
      jobName: props.defaultName
    };
  }

  private handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ jobName: e.target.value });
  };

  private handleConfirm = () => {
    const trimmedName = this.state.jobName.trim();
    if (trimmedName) {
      this.props.onConfirm(trimmedName);
    }
  };

  private handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      this.handleConfirm();
    } else if (e.key === 'Escape') {
      this.props.onCancel();
    }
  };

  render(): React.ReactElement {
    const { jobName } = this.state;
    const isValid = jobName.trim().length > 0;

    return (
      <div className="trainwave-job-name-dialog">
        <div className="trainwave-job-name-content">
          <div className="trainwave-job-name-field">
            <label htmlFor="job-name-input">Job Name</label>
            <input
              id="job-name-input"
              type="text"
              value={jobName}
              onChange={this.handleNameChange}
              onKeyDown={this.handleKeyPress}
              placeholder="Enter job name..."
              autoFocus
              className="trainwave-job-name-input"
            />
          </div>
        </div>

        <div className="trainwave-job-name-footer">
          <button
            className="trainwave-job-name-button trainwave-job-name-button-secondary"
            onClick={this.props.onCancel}
          >
            Cancel
          </button>
          <button
            className="trainwave-launch-job-button"
            onClick={this.handleConfirm}
            disabled={!isValid}
          >
            <span className="trainwave-button-icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                strokeWidth={1.5}
                className="trainwave-icon trainwave-icon-white"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z"
                />
              </svg>
            </span>
            Launch Job
          </button>
        </div>
      </div>
    );
  }
}

export function showJobNameDialog(defaultName: string): Promise<string | null> {
  return new Promise<string | null>(resolve => {
    let result: string | null = null;

    const dialog = new Dialog({
      title: 'Launch Training Job',
      body: React.createElement(JobNameDialog, {
        defaultName,
        onConfirm: (jobName: string) => {
          result = jobName;
          dialog.close();
        },
        onCancel: () => {
          result = null;
          dialog.close();
        }
      }),
      buttons: [],
      focusNodeSelector: '.trainwave-job-name-input'
    });

    dialog
      .launch()
      .then(() => {
        resolve(result);
      })
      .catch(error => {
        console.error('Dialog error:', error);
        resolve(null);
      });
  });
}
