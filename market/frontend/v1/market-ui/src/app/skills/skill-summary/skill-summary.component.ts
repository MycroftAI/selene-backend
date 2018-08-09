import { Component, Input, OnInit } from '@angular/core';

import { faComment, faMicrophoneAlt } from '@fortawesome/free-solid-svg-icons';
import { SkillsService } from "../skills.service";

@Component({
  selector: 'market-skill-summary',
  templateUrl: './skill-summary.component.html',
  styleUrls: ['./skill-summary.component.scss']
})
export class SkillSummaryComponent implements OnInit {
    public skillIcon = faMicrophoneAlt;
    @Input() public skills;
    public voiceIcon = faComment;

    constructor(private skillsService: SkillsService) { }

    ngOnInit() { }

    install_skill(skill) {
        this.skillsService.installSkill().subscribe(
            (response) => {this.onInstallSuccess(response)},
            (response) => {this.onInstallFailure(response)}
        );
    }

    onInstallSuccess(response) {
        console.log('success!')
    }

    onInstallFailure(response) {
        window.location.assign('http://login.mycroft.test');
    }
}
