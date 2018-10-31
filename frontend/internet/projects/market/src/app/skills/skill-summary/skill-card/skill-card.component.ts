/**
 * Format the header portion of a skill summary card.  This includes the icon
 * for the skill and a Mycroft logo if the skill is authored by Mycroft AI.
 */
import { Component, Input, OnInit} from '@angular/core';
import { MatSnackBar } from '@angular/material';

import { faComment } from '@fortawesome/free-solid-svg-icons';

import { AvailableSkill } from '../../skills.service';
import { InstallService } from '../../install.service';

const fiveSeconds = 5000;

@Component({
    selector: 'market-skill-card',
    templateUrl: './skill-card.component.html',
    styleUrls: ['./skill-card.component.scss']
})
export class SkillCardComponent implements OnInit {
    @Input() public skill: AvailableSkill;
    public voiceIcon = faComment;

    constructor(
        public installSnackbar: MatSnackBar,
        private installService: InstallService) {

    }

    ngOnInit() {
        this.installService.statusNotifications.subscribe(
            (statusChange) => {
                this.showStatusNotifications(statusChange);
            }
        );
    }

    showStatusNotifications(statusChange: string[]) {
        let notificationMessage: string;
        const [skillName, notificationStatus] = statusChange;
        if (this.skill.name === skillName) {
            switch (notificationStatus) {
                case ('installed'): {
                    notificationMessage = 'The ' + this.skill.title + ' skill has ' +
                        'been added to all your devices.';
                    this.showInstallStatusNotification(notificationMessage);
                    break;
                }
                case ('uninstalled'): {
                    notificationMessage = 'The ' + this.skill.title + ' skill has ' +
                        'been removed from all your devices.';
                    this.showInstallStatusNotification(notificationMessage);
                    break;
                }
                case ('install failed'): {
                    notificationMessage = 'The ' + this.skill.title + ' failed to ' +
                        'install to one or more of your devices.  Install will be ' +
                        'retried until successful';
                    this.showInstallStatusNotification(notificationMessage);
                    break;
                }
                case ('uninstall failed'): {
                    notificationMessage = 'The ' + this.skill.title + ' failed to ' +
                        'uninstall from one or more of your devices.  Uninstall ' +
                        'will be retried until successful';
                    this.showInstallStatusNotification(notificationMessage);
                }
            }
        }
    }

    showInstallStatusNotification(notificationMessage: string) {
        this.installSnackbar.open(
            notificationMessage,
            '',
            {panelClass: 'login-snackbar', duration: fiveSeconds}
        );
    }
}
