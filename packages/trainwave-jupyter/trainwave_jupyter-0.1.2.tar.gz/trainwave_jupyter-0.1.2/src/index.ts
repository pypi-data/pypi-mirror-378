import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { INotebookTracker } from '@jupyterlab/notebook';

import { requestAPI } from './handler';
import { AuthService, AuthConfig } from './auth';
import { showAuthDialog } from './auth-dialog';
import { showSettingsDialog } from './settings-dialog';
import { TrainwaveDropdown } from './dropdown';
import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';

/**
 * Initialization data for the trainwave extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'trainwave-jupyter:plugin',
  description:
    'Make trainwave.ai available right in your notebook for fast, cheap and efficient GPU workloads.',
  autoStart: true,
  requires: [INotebookTracker],
  optional: [ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    settingRegistry: ISettingRegistry | null
  ) => {
    console.log('JupyterLab extension trainwave is activated!');

    // Initialize authentication service
    const authConfig: AuthConfig = {
      endpoint: 'https://backend.trainwave.ai', // Trainwave API endpoint
      polling_timeout: 300, // 5 minutes timeout
      polling_interval: 2 // Poll every 2 seconds
    };

    let authService: AuthService | null = null;
    let settings: ISettingRegistry.ISettings | null = null;

    // Function to initialize auth service and update toolbars
    const initializeAuthService = (service: AuthService) => {
      authService = service;
      console.log(
        'Auth service initialized, isAuthenticated:',
        service.isAuthenticated()
      );
      // Update all existing toolbars
      notebookTracker.forEach(panel => {
        updateToolbarForPanel(panel);
      });
    };

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(loadedSettings => {
          settings = loadedSettings;
          const service = new AuthService(authConfig, settings);
          console.log('trainwave settings loaded:', settings.composite);
          initializeAuthService(service);
        })
        .catch(reason => {
          console.error('Failed to load settings for trainwave.', reason);
          // Create auth service without settings
          const service = new AuthService(authConfig);
          initializeAuthService(service);
        });
    } else {
      // Create auth service without settings
      const service = new AuthService(authConfig);
      initializeAuthService(service);
    }

    requestAPI<any>('get-example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The trainwave server extension appears to be missing.\n${reason}`
        );
      });

    // Add command for trainwave authentication
    app.commands.addCommand('trainwave-jupyter:auth', {
      label: 'Trainwave Authentication',
      execute: async () => {
        console.log('Trainwave authentication triggered!');

        if (!authService) {
          console.error('Auth service not initialized');
          return;
        }

        try {
          // Show authentication dialog
          await showAuthDialog(authService);

          // Check if user is now authenticated
          if (authService.isAuthenticated()) {
            console.log('User is authenticated with Trainwave');
            // Update all toolbars to show the dropdown
            notebookTracker.forEach(panel => {
              updateToolbarForPanel(panel);
            });
          }
        } catch (error) {
          console.error('Authentication failed:', error);
          alert(
            `Authentication failed: ${error instanceof Error ? error.message : 'Unknown error'}`
          );
        }
      }
    });

    // Function to update toolbar for a specific panel
    const updateToolbarForPanel = (panel: any) => {
      const toolbar = panel.toolbar;
      console.log(
        'Updating toolbar for panel, authService exists:',
        !!authService,
        'isAuthenticated:',
        authService?.isAuthenticated()
      );

      // Remove existing trainwave buttons if they exist
      try {
        toolbar.removeItem('trainwave-button');
      } catch (e) {
        // Button doesn't exist, that's fine
      }
      try {
        toolbar.removeItem('trainwave-dropdown');
      } catch (e) {
        // Dropdown doesn't exist, that's fine
      }

      // Only show dropdown widget if authService is available
      if (authService) {
        const dropdownWidget = ReactWidget.create(
          React.createElement(TrainwaveDropdown, {
            authService: authService,
            notebookTracker: notebookTracker,
            onSettingsClick: () => {
              if (authService) {
                showSettingsDialog(authService);
              }
            },
            onLoginClick: () => {
              if (authService) {
                showAuthDialog(authService);
              }
            }
          })
        );
        dropdownWidget.addClass('trainwave-dropdown-widget');
        toolbar.insertItem(10, 'trainwave-dropdown', dropdownWidget);
      }
    };

    // Add dropdown to existing notebooks (only when authService is ready)
    if (authService) {
      notebookTracker.forEach(panel => {
        updateToolbarForPanel(panel);
      });
    }

    // Add dropdown to new notebooks
    notebookTracker.widgetAdded.connect((sender, panel) => {
      // Update the toolbar once authService is ready
      if (authService) {
        setTimeout(() => updateToolbarForPanel(panel), 100);
      }
    });

    // Global function to update all toolbars (for use after auth changes)
    (window as any).updateTrainwaveToolbars = () => {
      if (authService) {
        notebookTracker.forEach(panel => {
          updateToolbarForPanel(panel);
        });
      }
    };
  }
};

export default plugin;
