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
    public voiceIcon = faComment;

    constructor(public loginSnackbar: MatSnackBar, private skillsService: SkillsService) { }

    ngOnInit() { }

    install_skill(skill: Skill) : void {
        this.skillsService.installSkill(skill).subscribe(
            (response) => {
                this.onInstallSuccess(response)
            },
            (response) => {
                this.onInstallFailure(response)
            }
        );
    }

    onInstallSuccess(response) : void {
        console.log('success!')
    }

    onInstallFailure(response) : void {
        if (response.status === 401) {
            this.loginSnackbar.open(
                'To install a skill, log in to your account.',
                'LOG IN',
                {panelClass: 'mycroft-snackbar', duration: 5000}

            );
        }
    }
}
