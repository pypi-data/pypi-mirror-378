import React from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { AuthService } from './auth';
import { OrganizationSelector } from './organization-selector';

interface AuthDialogProps {
  authService: AuthService;
  onAuthSuccess?: () => void;
  onAuthError?: (error: string) => void;
}

export class AuthDialog extends React.Component<
  AuthDialogProps,
  {
    isLoading: boolean;
    error: string | null;
    showOrganizationSelector: boolean;
  }
> {
  constructor(props: AuthDialogProps) {
    super(props);
    this.state = {
      isLoading: false,
      error: null,
      showOrganizationSelector: false
    };
  }

  private _handleAuthenticate = async () => {
    this.setState({ isLoading: true, error: null });

    try {
      const success = await this.props.authService.authenticate();
      if (success) {
        // Check if user already has an organization selected
        const settings = this.props.authService.loadSettings();
        if (settings.organization_id) {
          // User already has organization selected, proceed normally
          this.props.onAuthSuccess?.();
          // Refresh dropdown to show authenticated state
          if ((window as any).refreshTrainwaveDropdown) {
            (window as any).refreshTrainwaveDropdown();
          }
          // Close the dialog
          const dialog = document.querySelector('.jp-Dialog') as HTMLElement;
          if (dialog) {
            dialog.click();
          }
        } else {
          // User needs to select an organization
          this.setState({ showOrganizationSelector: true });
        }
      } else {
        this.setState({ error: 'Authentication failed' });
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Authentication failed';
      this.setState({ error: errorMessage });
      this.props.onAuthError?.(errorMessage);
    } finally {
      this.setState({ isLoading: false });
    }
  };

  private _handleOrganizationSelected = (organizationId: string) => {
    // Organization has been selected and saved, proceed with success
    this.props.onAuthSuccess?.();
  };

  private _handleLogout = async () => {
    try {
      await this.props.authService.logout();
      // Trigger UI update to reflect logout state
      if ((window as any).updateTrainwaveToolbars) {
        (window as any).updateTrainwaveToolbars();
      }
      // Refresh dropdown to show logged out state
      if ((window as any).refreshTrainwaveDropdown) {
        (window as any).refreshTrainwaveDropdown();
      }
      this.props.onAuthSuccess?.();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  render(): React.ReactElement {
    const { isLoading, error, showOrganizationSelector } = this.state;
    const isAuthenticated = this.props.authService.isAuthenticated();

    // Show organization selector if user just authenticated and needs to select organization
    if (showOrganizationSelector) {
      return (
        <OrganizationSelector
          authService={this.props.authService}
          onOrganizationSelected={this._handleOrganizationSelected}
        />
      );
    }

    return (
      <div className="trainwave-auth-dialog">
        <div className="trainwave-auth-header">
          <h3>Trainwave Authentication</h3>
          <p>Connect your Trainwave account to access GPU workloads</p>
        </div>

        {error && (
          <div className="trainwave-auth-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="trainwave-auth-content">
          {isAuthenticated ? (
            <div className="trainwave-auth-success">
              <div className="trainwave-auth-status">
                <span className="trainwave-auth-icon">✓</span>
                <span>You are authenticated with Trainwave</span>
              </div>
              <button
                className="trainwave-auth-button trainwave-auth-button-secondary"
                onClick={this._handleLogout}
                disabled={isLoading}
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="trainwave-auth-login">
              <div className="trainwave-auth-info">
                <p>
                  To use Trainwave features, you need to authenticate with your
                  account. This will open a browser window for you to complete
                  the login.
                </p>
                <ul>
                  <li>Access to GPU workloads</li>
                  <li>Manage your compute resources</li>
                  <li>Track usage and billing</li>
                  <li>Secure session-based authentication</li>
                </ul>
              </div>
              <button
                className="trainwave-auth-button trainwave-auth-button-primary"
                onClick={this._handleAuthenticate}
                disabled={isLoading}
              >
                {isLoading
                  ? 'Authenticating...'
                  : 'Authenticate with Trainwave'}
              </button>
            </div>
          )}
        </div>

        <div className="trainwave-auth-footer">
          <p>
            <a
              href="https://trainwave.ai"
              target="_blank"
              rel="noopener noreferrer"
            >
              Learn more about Trainwave
            </a>
          </p>
        </div>
      </div>
    );
  }
}

/**
 * Show the authentication dialog
 */
export function showAuthDialog(authService: AuthService): Promise<void> {
  return new Promise((resolve, reject) => {
    let resolved = false;

    const dialog = new Dialog({
      title: 'Setup',
      body: React.createElement(AuthDialog, {
        authService,
        onAuthSuccess: () => {
          if (!resolved) {
            resolved = true;
            console.log('Authentication successful, updating toolbars...');
            // Update toolbars after successful authentication
            if ((window as any).updateTrainwaveToolbars) {
              (window as any).updateTrainwaveToolbars();
            } else {
              console.warn('updateTrainwaveToolbars function not found');
            }
            // Refresh dropdown to show authenticated state
            if ((window as any).refreshTrainwaveDropdown) {
              (window as any).refreshTrainwaveDropdown();
            }
            dialog.resolve();
            resolve();
          }
        },
        onAuthError: error => {
          if (!resolved) {
            resolved = true;
            dialog.reject();
            reject(new Error(error));
          }
        }
      }),
      buttons: [Dialog.cancelButton({ label: 'Close' })],
      focusNodeSelector: '.trainwave-auth-button-primary'
    });

    dialog
      .launch()
      .then(() => {
        if (!resolved) {
          resolved = true;
          resolve();
        }
      })
      .catch(error => {
        if (!resolved) {
          resolved = true;
          reject(error);
        }
      });
  });
}
