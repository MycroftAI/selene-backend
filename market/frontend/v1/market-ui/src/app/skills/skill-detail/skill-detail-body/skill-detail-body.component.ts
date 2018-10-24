import { Component, Input } from '@angular/core';

import { SkillDetail } from "../../skills.service";
import { faComment } from "@fortawesome/free-solid-svg-icons";

@Component({
  selector: 'market-skill-detail-body',
  templateUrl: './skill-detail-body.component.html',
  styleUrls: ['./skill-detail-body.component.scss']
})
export class SkillDetailBodyComponent {
    @Input() public skill: SkillDetail;
    public triggerIcon = faComment;

    constructor() { }

}
