import { Component, Input, OnInit } from '@angular/core';
import { MatSnackBar } from "@angular/material";

import { faComment } from '@fortawesome/free-solid-svg-icons';

import { SkillsService, Skill } from "../skills.service";

@Component({
    selector: 'market-skill-summary',
    templateUrl: './skill-summary.component.html',
    styleUrls: ['./skill-summary.component.scss'],
})
export class SkillSummaryComponent implements OnInit {
    @Input() public skills: Skill[];
    private skillToInstall: Skill;
    public voiceIcon = faComment;

    constructor(public loginSnackbar: MatSnackBar, private skillsService: SkillsService) { }

    ngOnInit() { }

    /**
     * Install a skill onto one or many devices
     *
     * @param {Skill} skill
     */
    install_skill(skill: Skill) : void {
        this.skillToInstall = skill;
        this.skillsService.installSkill(skill).subscribe(
            (response) => {
                this.onInstallSuccess(response)
            },
            (response) => {
                this.onInstallFailure(response)
            }
        );
    }

    /**
     * Handle the successful install attempt
     *
     * This does not indicate that the install of the skill completed, only
     * that the request to install a skill succeeded.  Change the install
     * button to an "installing" state.
     *
     * @param response
     */
    onInstallSuccess(response) : void {
        console.log('success!')
    }

    /**
     * Handle the failure to install a skill.
     *
     * If a user attempts to install a skill without being logged in, show a
     * snackbar to notify the user and give them the ability to log in.
     *
     * @param response - object representing the response from the API call
     */
    onInstallFailure(response) : void {
        if (response.status === 401) {
            let skillNameParts = this.skillToInstall.skill_name.split('-');
            let installName = [];
            skillNameParts.forEach(
                (part) => {
                    if (part.toLowerCase() != 'mycroft' && part.toLowerCase() != 'skill') {
                        installName.push(part);
                    }
                }
            );
            this.loginSnackbar.open(
                'Skill installation functionality coming soon.  ' +
                    'In the meantime use your voice to install skills ' +
                    'by saying: "Hey Mycroft, install ' + installName.join(' ') + '"',
                '',
                {panelClass: 'mycroft-snackbar', duration: 5000}

            );

            // This is the snackbar logic for when the login and install
            // functionality is in place
            //
            // this.loginSnackbar.open(
            //     'To install a skill, log in to your account.',
            //     'LOG IN',
            //     {panelClass: 'mycroft-snackbar', duration: 5000}
            //
            // );
        }
    }
}
