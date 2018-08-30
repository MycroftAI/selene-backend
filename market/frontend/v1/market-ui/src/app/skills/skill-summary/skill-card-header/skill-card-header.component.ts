/**
 * Format the header portion of a skill summary card.  This includes the icon
 * for the skill and a Mycroft logo if the skill is authored by Mycroft AI.
 */
import { Component, Input, OnInit } from '@angular/core';
import { Skill } from "../../skills.service";
import { faMicrophoneAlt } from "@fortawesome/free-solid-svg-icons";

@Component({
    selector: 'market-skill-card-header',
    templateUrl: './skill-card-header.component.html',
    styleUrls: ['./skill-card-header.component.scss']
})
export class SkillCardHeaderComponent implements OnInit {
    public skillIcon = faMicrophoneAlt;
    @Input() public skill: Skill;
    public isMycroftMade: boolean;

    constructor() { }

    /**
     * Include the Mycroft AI logo in the card header if Mycroft authored the skill
     */
    ngOnInit() {
        this.isMycroftMade = this.skill.author.toLowerCase().includes('mycroft')
    }

}
