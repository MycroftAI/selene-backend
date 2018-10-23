/**
 * Format the header portion of a skill summary card.  This includes the icon
 * for the skill and a Mycroft logo if the skill is authored by Mycroft AI.
 */
import { Component, Input } from '@angular/core';
import { AvailableSkill } from "../../skills.service";
import { faComment } from "@fortawesome/free-solid-svg-icons";

@Component({
    selector: 'market-skill-card',
    templateUrl: './skill-card.component.html',
    styleUrls: ['./skill-card.component.scss']
})
export class SkillCardComponent {
    @Input() public skill: AvailableSkill;
    public voiceIcon = faComment;

    constructor() { }
}
