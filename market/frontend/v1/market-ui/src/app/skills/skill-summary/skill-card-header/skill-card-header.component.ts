/**
 * Format the header portion of a skill summary card.  This includes the icon
 * for the skill and a Mycroft logo if the skill is authored by Mycroft AI.
 */
import { Component, Input, OnInit } from '@angular/core';
import { Skill } from "../../skills.service";
import { faCheckCircle } from "@fortawesome/free-solid-svg-icons";

@Component({
    selector: 'market-skill-card-header',
    templateUrl: './skill-card-header.component.html',
    styleUrls: ['./skill-card-header.component.scss']
})
export class SkillCardHeaderComponent implements OnInit {
    @Input() public skill: Skill;
    public isMycroftMade: boolean;
    public isInstalled: boolean;
    public installedIcon = faCheckCircle;

    constructor() { }

    /**
     * Include the Mycroft AI logo in the card header if Mycroft authored the skill
     */
    ngOnInit() {
        if (this.skill.credits) {
            this.isMycroftMade = this.skill.credits[0]['name'] == 'Mycroft AI';
        }
        if (this.skill.installStatus === 'installed') {
            this.isInstalled = true;
        }
    }
}
