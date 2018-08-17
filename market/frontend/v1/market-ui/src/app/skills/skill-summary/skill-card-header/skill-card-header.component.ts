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

    ngOnInit() {
        this.isMycroftMade = this.skill.author.toLowerCase().includes('mycroft')
    }

}
